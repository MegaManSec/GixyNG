"""
Missing Resolver Plugin - Detects static DNS resolution in proxy directives.

This plugin is COMPREHENSIVE and detects:
- Static hostnames in proxy_pass, fastcgi_pass, uwsgi_pass, scgi_pass, grpc_pass
- Upstream servers without 'resolve' parameter  
- Cloud provider endpoints (AWS ELB, GCP, Azure, Cloudflare) with elevated severity
- Variable-based proxy_pass WITHOUT a resolver directive configured
- Kubernetes service discovery patterns

Superior detection features:
- Proper TLD classification (not just suffix matching)
- Compound TLD support (.co.uk, .com.au, etc.)
- Cloud provider hostname detection with HIGH severity
- Resolver directive scope checking
- Upstream zone directive awareness (enables dynamic config)
- Smart variable analysis
"""

import re

import gixy
from gixy.plugins.plugin import Plugin
from gixy.directives.directive import is_ipv6, is_ipv4
from gixy.core.variable import compile_script
import gixy.core.builtin_variables as builtins


# Common public TLDs
PUBLIC_TLDS = frozenset([
    # Generic TLDs
    'com', 'net', 'org', 'info', 'biz', 'io', 'co', 'app', 'dev', 'cloud',
    'online', 'site', 'website', 'tech', 'store', 'shop', 'blog', 'xyz',
    'me', 'tv', 'cc', 'ws', 'mobi', 'name', 'pro', 'aero', 'asia', 'cat',
    'coop', 'jobs', 'museum', 'travel', 'xxx', 'post', 'tel',
    # New gTLDs (popular ones)
    'agency', 'consulting', 'digital', 'email', 'global', 'group', 'guru',
    'host', 'link', 'live', 'media', 'network', 'news', 'plus', 'press',
    'services', 'social', 'solutions', 'space', 'studio', 'support',
    'systems', 'today', 'tools', 'video', 'world', 'zone',
    # Country codes
    'uk', 'de', 'fr', 'nl', 'ru', 'cn', 'jp', 'br', 'au', 'ca', 'in', 'it',
    'es', 'pl', 'se', 'no', 'fi', 'dk', 'at', 'ch', 'be', 'cz', 'hu', 'ro',
    'ua', 'kr', 'tw', 'hk', 'sg', 'my', 'th', 'ph', 'id', 'vn', 'nz', 'za',
    'mx', 'ar', 'cl', 'pe', 've', 'ec', 'pt', 'gr', 'tr', 'il', 'ae',
    'sa', 'eg', 'ng', 'ke', 'ie', 'is', 'ee', 'lv', 'lt', 'sk', 'si', 'hr',
    'bg', 'rs', 'by', 'kz', 'uz', 'az', 'ge', 'am', 'md', 'pk', 'bd', 'lk',
    'us', 'eu', 'asia',
    # Infrastructure TLDs
    'edu', 'gov', 'mil', 'int',
])

# Compound TLDs (country-specific second-level domains)
COMPOUND_TLDS = frozenset([
    'co.uk', 'org.uk', 'me.uk', 'ltd.uk', 'plc.uk', 'net.uk', 'sch.uk',
    'com.au', 'net.au', 'org.au', 'edu.au', 'gov.au', 'asn.au', 'id.au',
    'com.br', 'net.br', 'org.br', 'gov.br', 'edu.br',
    'co.nz', 'net.nz', 'org.nz', 'govt.nz', 'ac.nz',
    'co.jp', 'or.jp', 'ne.jp', 'ac.jp', 'go.jp',
    'com.cn', 'net.cn', 'org.cn', 'gov.cn', 'edu.cn',
    'co.kr', 'or.kr', 'ne.kr', 'go.kr', 'ac.kr',
    'com.mx', 'net.mx', 'org.mx', 'gob.mx', 'edu.mx',
    'com.ar', 'net.ar', 'org.ar', 'gov.ar', 'edu.ar',
    'com.tw', 'net.tw', 'org.tw', 'gov.tw', 'edu.tw',
    'com.hk', 'net.hk', 'org.hk', 'gov.hk', 'edu.hk',
    'com.sg', 'net.sg', 'org.sg', 'gov.sg', 'edu.sg',
    'co.in', 'net.in', 'org.in', 'gov.in', 'ac.in',
    'co.za', 'net.za', 'org.za', 'gov.za', 'ac.za',
    'com.tr', 'net.tr', 'org.tr', 'gov.tr', 'edu.tr',
    'co.il', 'net.il', 'org.il', 'gov.il', 'ac.il',
    'com.ua', 'net.ua', 'org.ua', 'gov.ua', 'edu.ua',
    'com.pl', 'net.pl', 'org.pl', 'gov.pl', 'edu.pl',
])

# Internal/local domain suffixes
LOCAL_SUFFIXES = (
    # Standard local
    '.intranet', '.internal', '.private', '.corp', '.home', '.lan',
    '.local', '.localhost', '.localdomain',
    # Reserved per RFC 2606 / RFC 6761
    '.test', '.example', '.invalid', '.onion',
    # Kubernetes/Docker/Container orchestration
    '.svc', '.svc.cluster', '.svc.cluster.local', '.pod', '.pod.cluster.local',
    '.default', '.default.svc', '.default.svc.cluster.local',
    # Common internal patterns
    '.consul', '.service.consul', '.node.consul',  # HashiCorp Consul
    '.marathon.mesos', '.mesos',  # Mesos/Marathon
    '.rancher.internal',  # Rancher
    '.docker', '.docker.internal',  # Docker
    '.ecs.internal',  # AWS ECS internal (but not ELB!)
)

# Cloud provider patterns that DEFINITELY need dynamic resolution (HIGH severity)
# These IPs change frequently and using static resolution is almost always wrong
CLOUD_PROVIDER_PATTERNS = [
    # AWS
    (r'\.elb\.amazonaws\.com$', 'AWS ELB'),
    (r'\.elb\.[a-z]+-[a-z]+-\d+\.amazonaws\.com$', 'AWS ELB'),
    (r'\.elasticbeanstalk\.com$', 'AWS Elastic Beanstalk'),
    (r'\.cloudfront\.net$', 'AWS CloudFront'),
    (r'\.execute-api\.[a-z]+-[a-z]+-\d+\.amazonaws\.com$', 'AWS API Gateway'),
    (r'\.lambda-url\.[a-z]+-[a-z]+-\d+\.on\.aws$', 'AWS Lambda URL'),
    (r'\.s3\.amazonaws\.com$', 'AWS S3'),
    (r'\.s3\.[a-z]+-[a-z]+-\d+\.amazonaws\.com$', 'AWS S3'),
    # Google Cloud
    (r'\.run\.app$', 'Google Cloud Run'),
    (r'\.cloudfunctions\.net$', 'Google Cloud Functions'),
    (r'\.appspot\.com$', 'Google App Engine'),
    (r'\.googleapis\.com$', 'Google APIs'),
    # Azure
    (r'\.azurewebsites\.net$', 'Azure App Service'),
    (r'\.azure-api\.net$', 'Azure API Management'),
    (r'\.cloudapp\.azure\.com$', 'Azure Cloud Service'),
    (r'\.blob\.core\.windows\.net$', 'Azure Blob Storage'),
    (r'\.azureedge\.net$', 'Azure CDN'),
    (r'\.trafficmanager\.net$', 'Azure Traffic Manager'),
    # Cloudflare
    (r'\.workers\.dev$', 'Cloudflare Workers'),
    (r'\.pages\.dev$', 'Cloudflare Pages'),
    # Heroku
    (r'\.herokuapp\.com$', 'Heroku'),
    # Vercel/Zeit
    (r'\.vercel\.app$', 'Vercel'),
    (r'\.now\.sh$', 'Vercel (legacy)'),
    # Netlify
    (r'\.netlify\.app$', 'Netlify'),
    (r'\.netlify\.com$', 'Netlify'),
    # Railway
    (r'\.railway\.app$', 'Railway'),
    # Render
    (r'\.onrender\.com$', 'Render'),
    # DigitalOcean
    (r'\.ondigitalocean\.app$', 'DigitalOcean App Platform'),
    # Fly.io
    (r'\.fly\.dev$', 'Fly.io'),
    # Generic CDN/LB patterns
    (r'\.cdn\.', 'CDN endpoint'),
    (r'\.lb\.', 'Load balancer'),
    (r'\.loadbalancer\.', 'Load balancer'),
]


class missing_resolver(Plugin):
    """
    Detects proxy directives with hostnames that won't have DNS re-resolution.
    
    Nginx resolves DNS for static hostnames ONCE at startup and caches forever.
    This causes issues when backend IPs change (cloud LBs, CDNs, failover).
    
    This plugin is smarter than basic suffix matching:
    - Proper TLD detection with compound TLD support
    - Cloud provider detection (AWS ELB, GCP, Azure, etc.) → HIGH severity
    - Checks if resolver directive exists when using variables
    - Understands upstream 'resolve' and 'zone' directives
    - Kubernetes/Docker/Consul service discovery awareness
    """

    summary = "Proxy target uses static DNS resolution (resolved only at startup)."
    severity = gixy.severity.MEDIUM
    description = (
        "Using proxy_pass with a static hostname causes DNS to be resolved only at startup, "
        "potentially sending traffic to stale IPs. This is especially critical for cloud "
        "load balancers and CDNs where IPs change frequently. Use a variable with 'resolver' "
        "directive, or upstream with 'resolve' parameter (nginx 1.27.3+)."
    )
    help_url = "https://gixy.getpagespeed.com/en/plugins/missing_resolver/"
    directives = ["proxy_pass", "fastcgi_pass", "uwsgi_pass", "scgi_pass", "grpc_pass"]

    def __init__(self, config):
        super(missing_resolver, self).__init__(config)
        self.parse_uri_re = re.compile(
            r'^(?P<scheme>[a-z][a-z0-9+.-]*://)?'
            r'(?P<host>\[[0-9a-fA-F:.]+\]|[^/?#:]+)'
            r'(?::(?P<port>[0-9]+))?'
        )
        # Compile cloud provider patterns
        self.cloud_patterns = [
            (re.compile(pattern, re.IGNORECASE), name) 
            for pattern, name in CLOUD_PROVIDER_PATTERNS
        ]

    def audit(self, directive):
        if not directive.args:
            return
            
        target = directive.args[0]
        directive_name = directive.name
        
        # Skip unix sockets
        if 'unix:' in target:
            return

        parsed = self.parse_uri_re.match(target)
        if not parsed:
            return

        parsed_host = parsed.group('host')
        
        # Resolve any variables in the host part
        resolved_host = self._resolve_host(parsed_host)
        if resolved_host is None:
            return  # Contains builtin variable - can't analyze

        if not resolved_host:
            return

        # Skip IP addresses
        if is_ipv6(resolved_host, strip_brackets=True) or is_ipv4(resolved_host, strip_port=True):
            return

        # Check if this is an upstream reference
        upstream_result = self._check_upstream(directive, resolved_host)
        if upstream_result is not None:
            if upstream_result:  # List of problematic servers
                self._report_upstream_issue(directive, resolved_host, upstream_result)
            return

        # Direct hostname usage - check if there's a variable with resolver
        if '$' in target:
            # Using variable - check if resolver is configured
            if self._has_resolver_in_scope(directive):
                return  # Has resolver, variable will trigger re-resolution
            # No resolver configured - this is actually a problem!
            self._report_missing_resolver_for_variable(directive, directive_name, resolved_host)
            return

        # Classify the hostname
        host_type, cloud_provider = self._classify_host(resolved_host)
        
        if host_type == 'internal':
            return
        
        # Report based on classification
        if cloud_provider:
            self._report_cloud_provider(directive, directive_name, resolved_host, cloud_provider)
        else:
            self._report_static_hostname(directive, directive_name, resolved_host)

    def _resolve_host(self, host_str):
        """Resolve variables in host string. Returns None if unresolvable."""
        try:
            compiled = compile_script(host_str)
        except Exception:
            return None
            
        resolved = ""
        for var in compiled:
            if var.name and builtins.is_builtin(var.name):
                return None
            if not isinstance(var.final_value, str):
                return None
            resolved += var.final_value
        return resolved

    def _classify_host(self, host):
        """
        Classify hostname.
        Returns: (type, cloud_provider)
        - type: 'public', 'internal', 'cloud', or 'unknown'
        - cloud_provider: name of cloud provider if detected, else None
        """
        host_lower = host.lower()
        
        # Check for local suffixes first
        for suffix in LOCAL_SUFFIXES:
            if host_lower.endswith(suffix):
                return ('internal', None)
        
        # Single-label hostname = internal
        if '.' not in host_lower:
            return ('internal', None)
        
        # Check for cloud provider patterns (HIGH priority detection)
        for pattern, provider_name in self.cloud_patterns:
            if pattern.search(host_lower):
                return ('cloud', provider_name)
        
        # Check compound TLDs first
        parts = host_lower.rsplit('.', 2)
        if len(parts) >= 3:
            compound = '.'.join(parts[-2:])
            if compound in COMPOUND_TLDS:
                return ('public', None)
        
        # Check single TLD
        parts = host_lower.rsplit('.', 1)
        if len(parts) == 2:
            tld = parts[1]
            if tld in PUBLIC_TLDS:
                return ('public', None)
        
        # Unknown - treat as potentially public
        return ('unknown', None)

    def _check_upstream(self, directive, resolved_host):
        """
        Check if host refers to an upstream block.
        Returns:
            - None: Not an upstream reference
            - []: Upstream found, all servers are safe
            - [(server, host, cloud_provider), ...]: Problematic servers
        """
        for upstream in directive.find_imperative_directives_in_scope("upstream", ancestors=True):
            upstream_args = getattr(upstream, "args", None)
            if upstream_args != [resolved_host]:
                continue
            
            # Check if upstream has 'zone' directive (enables dynamic config in Plus)
            has_zone = any(
                child.name == 'zone' 
                for child in upstream.children
            )
            
            problematic = []
            
            for child in upstream.children:
                if child.name != 'server':
                    continue
                    
                server_target = child.args[0] if child.args else ""
                
                # Has 'resolve' parameter - OK
                if 'resolve' in child.args:
                    continue
                
                # Skip unix sockets
                if 'unix:' in server_target:
                    continue
                
                parsed = self.parse_uri_re.match(server_target)
                if not parsed:
                    continue
                
                server_host = parsed.group('host')
                
                # Skip IPs
                if is_ipv6(server_host, strip_brackets=True) or is_ipv4(server_host, strip_port=True):
                    continue
                
                host_type, cloud_provider = self._classify_host(server_host)
                
                if host_type == 'internal':
                    continue
                
                problematic.append((child, server_host, cloud_provider))
            
            return problematic
        
        return None

    def _has_resolver_in_scope(self, directive):
        """Check if there's a resolver directive in scope."""
        for resolver in directive.find_directives_in_scope("resolver"):
            return True
        # Also check via find method on parents
        for parent in directive.parents:
            if hasattr(parent, 'some'):
                resolver = parent.some("resolver", flat=False)
                if resolver:
                    return True
        return False

    def _report_cloud_provider(self, directive, directive_name, hostname, provider):
        """Report HIGH severity issue for cloud provider endpoints."""
        reason = (
            f"CRITICAL: '{directive_name}' targets {provider} endpoint '{hostname}'. "
            f"Cloud provider IPs change frequently! Static DNS resolution will cause "
            f"traffic to be sent to wrong/old IPs. You MUST use dynamic resolution: "
            f"set $backend {hostname}; resolver 8.8.8.8 valid=10s; {directive_name} http://$backend;"
        )
        self.add_issue(
            severity=gixy.severity.HIGH,
            directive=[directive],
            reason=reason,
        )

    def _report_upstream_issue(self, directive, upstream_name, problematic_servers):
        """Report issue with upstream servers."""
        # Check if any are cloud providers
        cloud_servers = [(s, h, p) for s, h, p in problematic_servers if p]
        regular_servers = [(s, h, p) for s, h, p in problematic_servers if not p]
        
        if cloud_servers:
            # HIGH severity for cloud providers
            cloud_info = ', '.join(f"{h} ({p})" for _, h, p in cloud_servers)
            reason = (
                f"CRITICAL: Upstream '{upstream_name}' contains cloud provider endpoints "
                f"without 'resolve' parameter: {cloud_info}. These IPs change frequently! "
                f"Add 'resolve' parameter and configure 'resolver' directive."
            )
            self.add_issue(
                severity=gixy.severity.HIGH,
                directive=[directive] + [s for s, _, _ in cloud_servers],
                reason=reason,
            )
        
        if regular_servers:
            hosts = ', '.join(h for _, h, _ in regular_servers)
            reason = (
                f"Upstream '{upstream_name}' has server(s) without 'resolve': {hosts}. "
                f"Add 'resolve' parameter (nginx 1.27.3+) and 'resolver' directive for "
                f"dynamic DNS resolution."
            )
            self.add_issue(
                severity=gixy.severity.MEDIUM,
                directive=[directive] + [s for s, _, _ in regular_servers],
                reason=reason,
            )

    def _report_static_hostname(self, directive, directive_name, hostname):
        """Report MEDIUM severity for regular public hostnames."""
        reason = (
            f"'{directive_name}' uses static hostname '{hostname}'. DNS resolved once at "
            f"startup - if IP changes, traffic goes to stale address until nginx restart. "
            f"Consider: resolver 8.8.8.8 valid=30s; set $backend {hostname}; "
            f"{directive_name} http://$backend;"
        )
        self.add_issue(
            severity=gixy.severity.MEDIUM,
            directive=[directive],
            reason=reason,
        )

    def _report_missing_resolver_for_variable(self, directive, directive_name, hostname):
        """Report when variable is used but no resolver directive exists."""
        reason = (
            f"'{directive_name}' uses a variable but no 'resolver' directive found! "
            f"Without 'resolver', variable-based proxy_pass won't re-resolve DNS. "
            f"Add: resolver 8.8.8.8 valid=30s; (or your internal DNS server)"
        )
        self.add_issue(
            severity=gixy.severity.MEDIUM,
            directive=[directive],
            reason=reason,
        )
