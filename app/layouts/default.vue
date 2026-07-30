<template>
  <div :class="layoutCls">
    <aside v-if="showSidebar" class="rail">
      <NuxtLink to="/dashboard" class="rail-mark">
        <span class="rail-mark-name display">mechadealer</span>
        <span class="rail-mark-sub spec">NSE · BSE</span>
      </NuxtLink>

      <div class="tickrule tickrule--inverse rail-scale" />

      <nav class="rail-nav">
        <NuxtLink to="/dashboard" class="rail-link" active-class="is-active">
          <Icon name="mdi:view-dashboard-outline" class="rail-icon" />
          Dashboard
        </NuxtLink>
        <NuxtLink to="/strategies" class="rail-link" active-class="is-active">
          <Icon name="mdi:chart-line" class="rail-icon" />
          All strategies
        </NuxtLink>
      </nav>

      <div class="rail-group">
        <h2 class="spec rail-group-title">Your positions</h2>

        <ul v-if="userStore.strategies.length" class="rail-list">
          <li v-for="strategy in userStore.strategies" :key="strategy.id">
            <NuxtLink
              :to="`/strategies/${strategy.id}`"
              class="rail-sublink"
              active-class="is-active"
            >
              <span class="rail-sublink-name">{{ strategy.name }}</span>
              <span class="figure rail-sublink-value">{{
                formatCurrencyCompact(strategy.capital)
              }}</span>
            </NuxtLink>
          </li>
        </ul>

        <p v-else class="rail-empty">
          Nothing allocated yet.
          <NuxtLink to="/strategies" class="rail-empty-link">Browse strategies</NuxtLink>
        </p>
      </div>

      <p class="rail-foot spec">Market 09:15–15:30 IST</p>
    </aside>

    <main class="main">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from "vue";
import { useRoute } from "vue-router";

const route = useRoute();
const userStore = useUserStore();

const noSidebarRoutes = ["/", "/login", "/register"];
const showSidebar = computed(() => !noSidebarRoutes.includes(route.path));

const layoutCls = computed(() => ({
  shell: true,
  "shell--bare": !showSidebar.value,
}));

onMounted(async () => {
  await userStore.fetchUserStrategies();
});
</script>

<style scoped>
.shell {
  display: flex;
  min-height: 100vh;
  background: var(--panel);
}

.shell--bare .main {
  width: 100%;
}

/* --- Rail ---------------------------------------------------------------- */

.rail {
  width: var(--rail-w);
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  padding: 1.75rem 0 1.25rem;
  background: var(--ink);
  color: var(--text-inverse);
}

.rail-mark {
  display: block;
  padding: 0 1.25rem 1.25rem;
  text-decoration: none;
}

.rail-mark-name {
  display: block;
  font-size: 1.0625rem;
  color: var(--text-inverse);
}

.rail-mark-sub {
  display: block;
  margin-top: 0.375rem;
  color: var(--text-inverse-muted);
}

.rail-scale {
  margin: 0 1.25rem 1.5rem;
}

.rail-nav {
  display: flex;
  flex-direction: column;
  padding: 0 0.75rem;
  gap: 0.125rem;
}

.rail-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6875rem 0.75rem;
  border-radius: 2px;
  color: var(--text-inverse-muted);
  text-decoration: none;
  font-size: 0.9375rem;
  border-left: 2px solid transparent;
  transition: color 0.15s ease, background-color 0.15s ease,
    border-color 0.15s ease;
}

.rail-link:hover {
  color: var(--text-inverse);
  background: var(--ink-soft);
}

.rail-link.is-active {
  color: var(--text-inverse);
  background: var(--ink-soft);
  border-left-color: var(--brand-bright);
}

.rail-icon {
  font-size: 1.125rem;
  flex-shrink: 0;
}

/* --- Positions ----------------------------------------------------------- */

.rail-group {
  margin-top: 2rem;
  padding: 0 0.75rem;
  flex: 1;
  min-height: 0;
  overflow-y: auto;
}

.rail-group-title {
  padding: 0 0.75rem;
  margin: 0 0 0.75rem;
  color: var(--text-inverse-muted);
}

.rail-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.rail-sublink {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.5625rem 0.75rem;
  border-radius: 2px;
  border-left: 2px solid transparent;
  color: var(--text-inverse-muted);
  text-decoration: none;
  font-size: 0.875rem;
  transition: color 0.15s ease, background-color 0.15s ease,
    border-color 0.15s ease;
}

.rail-sublink:hover {
  color: var(--text-inverse);
  background: var(--ink-soft);
}

.rail-sublink.is-active {
  color: var(--text-inverse);
  background: var(--ink-soft);
  border-left-color: var(--brand-bright);
}

.rail-sublink-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rail-sublink-value {
  font-size: 0.75rem;
  flex-shrink: 0;
  color: var(--text-inverse-muted);
}

.rail-empty {
  margin: 0;
  padding: 0 0.75rem;
  font-size: 0.875rem;
  color: var(--text-inverse-muted);
  line-height: 1.5;
}

.rail-empty-link {
  display: block;
  margin-top: 0.25rem;
  color: var(--text-inverse);
  text-decoration: underline;
  text-underline-offset: 3px;
}

.rail-foot {
  margin: 1.5rem 0 0;
  padding: 1rem 2rem 0;
  border-top: 1px solid #262c32;
  color: var(--text-inverse-muted);
  font-size: 0.625rem;
}

/* --- Main ---------------------------------------------------------------- */

.main {
  flex: 1;
  min-width: 0;
  overflow-x: hidden;
}

/* --- Small screens: the rail becomes a header ---------------------------- */

@media (max-width: 52rem) {
  .shell {
    flex-direction: column;
  }

  .rail {
    width: 100%;
    padding: 1rem 0 0.75rem;
  }

  .rail-mark {
    padding-bottom: 0.875rem;
  }

  .rail-scale {
    margin-bottom: 0.875rem;
  }

  .rail-nav {
    flex-direction: row;
  }

  .rail-group {
    margin-top: 1rem;
    overflow: visible;
  }

  .rail-list {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .rail-sublink {
    border-left: none;
    border-bottom: 2px solid transparent;
  }

  .rail-sublink.is-active {
    border-left-color: transparent;
    border-bottom-color: var(--brand-bright);
  }

  .rail-foot {
    display: none;
  }
}
</style>
