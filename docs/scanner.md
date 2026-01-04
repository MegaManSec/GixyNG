# Online scanner

<div class="gixy-scan" data-gixy-scan>
  <div class="gixy-scan__controls">
    <textarea
      id="gixyConf"
      class="gixy-textarea"
      rows="10"
      placeholder="Paste nginx config here..."
      spellcheck="false"
    ></textarea>

    <div class="gixy-actions">
      <button id="gixyRun" class="md-button md-button--primary" type="button">Run</button>
      <span id="gixyStatus" class="gixy-status"></span>
    </div>
  </div>

  <div id="gixySummary" class="gixy-summary" hidden></div>
  <div id="gixyFilters" class="gixy-filters" hidden></div>
  <div id="gixyFindings" class="gixy-findings"></div>
</div>
