<template>
  <div class="landing">
    <header class="topbar">
      <span class="display topbar-mark">mechadealer</span>
      <NuxtLink to="/login" class="topbar-link">Sign in</NuxtLink>
    </header>

    <!-- The thesis: a rule fires and an order goes out without you watching.
         The record below is the shape of a real signal, not a performance claim. -->
    <section class="hero">
      <p class="spec hero-eyebrow">Automated trading · NSE &amp; BSE</p>

      <h1 class="display hero-line">
        EMA&nbsp;4 crosses EMA&nbsp;8.<br >
        The order goes out.<br >
        <span class="hero-line-quiet">You were not watching.</span>
      </h1>

      <figure class="record">
        <figcaption class="spec record-cap">Signal format</figcaption>
        <div class="tickrule record-scale" />
        <pre class="figure record-body">09:47:02 IST  IDEA.NSE  2M  EMA4&gt;EMA8  BUY 1 MARKET</pre>
      </figure>

      <div class="hero-actions">
        <NuxtLink to="/login" class="btn btn-primary">Sign in</NuxtLink>
        <NuxtLink to="/strategies" class="btn btn-outline">See the strategies</NuxtLink>
      </div>

      <p class="demo">
        <span class="spec">Demo account</span>
        <span class="figure demo-creds">demo / demo1234</span>
      </p>
    </section>

    <div class="tickrule tickrule--major band-rule" />

    <!-- A genuine pipeline, so the ordering carries information. -->
    <section class="pipeline">
      <h2 class="spec pipeline-title">What happens to your money</h2>

      <ol class="steps">
        <li v-for="step in steps" :key="step.n" class="step">
          <span class="figure step-n">{{ step.n }}</span>
          <div>
            <h3 class="step-title">{{ step.title }}</h3>
            <p class="step-body">{{ step.body }}</p>
          </div>
        </li>
      </ol>
    </section>

    <footer class="foot">
      <div class="tickrule foot-rule" />
      <div class="foot-inner">
        <span class="spec">mechadealer · {{ new Date().getFullYear() }}</span>
        <span class="spec">Market 09:15–15:30 IST</span>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
const steps = [
  {
    n: "01",
    title: "You allocate",
    body: "Put capital into a strategy. You are issued units at the strategy's current price, and you can withdraw them again at any time.",
  },
  {
    n: "02",
    title: "Market data arrives",
    body: "Bars stream in from the exchange every minute during market hours and are stored, then resampled onto each strategy's timeframe.",
  },
  {
    n: "03",
    title: "The rule fires",
    body: "Each strategy reads its own timeframe and emits a signal when its condition is met. No signal, no order.",
  },
  {
    n: "04",
    title: "The order is placed",
    body: "Signals become live broker orders, and fills are written back against the strategy so your position and P&L stay current.",
  },
];

definePageMeta({
  layout: "default",
});
</script>

<style scoped>
.landing {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* --- Top bar ------------------------------------------------------------- */

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.5rem var(--gutter);
  max-width: var(--max);
  width: 100%;
  margin: 0 auto;
}

.topbar-mark {
  font-size: 1.0625rem;
}

.topbar-link {
  font-family: var(--font-data);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--text);
  text-decoration: none;
  border-bottom: 1px solid var(--rule-strong);
  padding-bottom: 2px;
}

.topbar-link:hover {
  border-bottom-color: var(--ink);
}

/* --- Hero ---------------------------------------------------------------- */

.hero {
  max-width: var(--max);
  width: 100%;
  margin: 0 auto;
  padding: clamp(2rem, 5vw, 3.5rem) var(--gutter) clamp(2.5rem, 6vw, 4rem);
}

.hero-eyebrow {
  margin: 0 0 1.25rem;
}

.hero-line {
  font-size: clamp(1.875rem, 4.6vw, 3.375rem);
  margin: 0;
  max-width: 26ch;
  animation: rise 0.5s ease-out both;
}

.hero-line-quiet {
  color: var(--text-muted);
}

@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(0.5rem);
  }
}

/* --- Signal record ------------------------------------------------------- */

.record {
  margin: clamp(1.75rem, 4vw, 2.75rem) 0 0;
  max-width: 40rem;
}

.record-cap {
  display: block;
  margin-bottom: 0.5rem;
}

.record-scale {
  margin-bottom: 0.75rem;
}

.record-body {
  margin: 0;
  padding: 0;
  font-size: clamp(0.6875rem, 1.6vw, 0.875rem);
  color: var(--text);
  overflow-x: auto;
  white-space: pre;
}

/* --- Actions ------------------------------------------------------------- */

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: clamp(1.5rem, 3.5vw, 2.25rem);
}

.demo {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  margin: 1.5rem 0 0;
}

.demo-creds {
  font-size: 0.875rem;
  color: var(--text-muted);
}

/* --- Pipeline ------------------------------------------------------------ */

.band-rule,
.foot-rule {
  max-width: var(--max);
  width: 100%;
  margin: 0 auto;
}

.band-rule {
  margin-bottom: clamp(2.5rem, 6vw, 4rem);
}

.pipeline {
  max-width: var(--max);
  width: 100%;
  margin: 0 auto;
  padding: 0 var(--gutter) clamp(3rem, 8vw, 6rem);
  flex: 1;
}

.pipeline-title {
  margin: 0 0 2rem;
}

.steps {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr));
  gap: clamp(1.75rem, 4vw, 3rem);
}

.step {
  display: flex;
  gap: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--rule-strong);
}

.step-n {
  font-size: 0.75rem;
  color: var(--text-muted);
  flex-shrink: 0;
}

.step-title {
  font-size: 1.0625rem;
  margin: 0 0 0.4375rem;
}

.step-body {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--text-muted);
}

/* --- Foot ---------------------------------------------------------------- */

.foot-inner {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
  max-width: var(--max);
  width: 100%;
  margin: 0 auto;
  padding: 1rem var(--gutter) 2rem;
}
</style>
