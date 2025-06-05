<template>
  <div :class="layoutCls">
    <aside v-if="showSidebar" class="sidebar">
      <nav class="sidebar-nav">
        <NuxtLink to="/dashboard" class="nav-item" active-class="nav-item-active">
          <Icon name="mdi:view-dashboard-outline" class="icon" /> Dashboard
        </NuxtLink>
        <NuxtLink to="/strategies" class="nav-item" active-class="nav-item-active">
          <Icon name="mdi:chart-line" class="icon" /> All Strategies
        </NuxtLink>

        <div class="nav-section">
          <h3 class="nav-section-title">My Invested Strategies</h3>
          <ul v-if="userStore.strategies.length > 0" class="invested-strategies-list">
            <li v-for="strategy in userStore.strategies" :key="strategy.id">
              <NuxtLink :to="`/strategies/${strategy.id}`" class="nav-sub-item" active-class="nav-item-active">
                {{ strategy.name }}
              </NuxtLink>
            </li>
          </ul>
          <p v-else class="no-invested-strategies">No strategies invested yet.</p>
        </div>
      </nav>
    </aside>
    <main class="main-content">
      <slot />
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();

const noSidebarRoutes = ['/', '/login'];

const showSidebar = computed(() => {
  return !noSidebarRoutes.includes(route.path);
});

const layoutCls = computed(() => {
  return {
    'app-layout': true,
    'no-sidebar-layout': !showSidebar.value
  };
});

const userStore = useUserStore();

onMounted(async () => {
  // Fetch user data or strategies when the component mounts
  await userStore.fetchUserStrategies();
});

</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f0f2f5;
  font-family: 'Roboto', 'Arial', sans-serif;
}

.app-layout.no-sidebar-layout .main-content {
  margin-left: 0;
  width: 100%;
  /* Ensure main content takes full width */
}

.sidebar {
  width: 260px;
  background-color: #1A237E;
  /* Deep Indigo - Reverted to original */
  color: #E8EAF6;
  /* Lighter Indigo/Lavender for text for better contrast */
  padding: 20px 10px;
  /* Adjusted padding */
  border-right: 1px solid #283593;
  /* Slightly lighter Indigo for border */
  display: flex;
  flex-direction: column;
}

.sidebar-nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.nav-item,
.nav-sub-item {
  display: flex;
  align-items: center;
  padding: 12px 18px;
  /* Adjusted padding */
  color: #C5CAE9;
  /* Indigo accent - lighter for inactive text */
  text-decoration: none;
  border-radius: 6px;
  transition: background-color 0.2s ease, color 0.2s ease, padding-left 0.2s ease;
  font-size: 1em;
  font-weight: 500;
  /* Medium weight for readability */
}

.nav-item .icon {
  margin-right: 12px;
  font-size: 1.4em;
  /* Adjusted for SVG icons */
  min-width: 24px;
  /* Basic alignment */
  text-align: center;
  color: #AAB6FE;
  /* Lighter Indigo/Lavender for better visibility */
  opacity: 0.9;
  /* Slight opacity for non-active */
  transition: opacity 0.2s ease, transform 0.2s ease, color 0.2s ease;
  vertical-align: middle;
  /* Better alignment with text */
}

.nav-item:hover,
.nav-sub-item:hover {
  background-color: #283593;
  /* Indigo - for hover */
  color: #FFFFFF;
  /* White text on hover */
}

.nav-item:hover .icon,
.nav-sub-item:hover .icon {
  opacity: 1;
  transform: scale(1.1);
  color: #FFFFFF;
  /* White on hover for max contrast */
}

.nav-item-active {
  background-color: #FFC107;
  /* Amber - Reverted to original active color */
  color: #1A237E;
  /* Deep Indigo text for active amber background */
  font-weight: 600;
  /* Bolder for active */
}

.nav-item-active .icon {
  color: #1A237E;
  /* Deep Indigo to match text on Amber background */
  opacity: 1;
}


.nav-section {
  margin-top: 25px;
  padding-top: 15px;
  border-top: 1px solid #303F9F;
  /* Indigo shade for separator */
}

.nav-section-title {
  font-size: 0.88em;
  color: #9FA8DA;
  /* Lighter Indigo accent for section title */
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-bottom: 12px;
  padding-left: 18px;
  font-weight: 500;
}

.invested-strategies-list {
  list-style: none;
  padding-left: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.nav-sub-item {
  padding-left: 32px;
  /* Indent sub-items */
  font-size: 0.95em;
  color: #BDBDBD;
  /* Lighter grey for sub-items, ensure contrast */
}

.nav-sub-item:hover {
  color: #FFFFFF;
}

.nav-sub-item.nav-item-active {
  background-color: #FFA000;
  /* Darker Amber for active sub-item */
  color: #1A237E;
}


.no-invested-strategies {
  font-size: 0.9em;
  color: #9FA8DA;
  /* Lighter Indigo accent */
  padding: 10px 18px;
  font-style: italic;
}

.main-content {
  flex-grow: 1;
  padding: 0;
  overflow-y: auto;
  background-color: #f0f2f5;
  /* Reverted to original light grey */
}
</style>