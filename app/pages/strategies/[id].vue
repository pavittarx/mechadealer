<template>
  <div class="page-container">
    <div v-if="strategy">
      <h1>{{ strategy.name }}</h1>
      <p class="strategy-description">{{ strategy.description }}</p>

      <div class="details-grid">
        <div class="detail-item">
          <span class="label">Risk Level:</span>
          <span class="value">{{ strategy.riskLevel }}</span>
        </div>
        <div class="detail-item">
          <span class="label">Asset Class:</span>
          <span class="value">{{ strategy.assetClass }}</span>
        </div>
        <div class="detail-item">
          <span class="label">Minimum Investment:</span>
          <span class="value">{{ formatCurrency(strategy.minInvestment) }}</span>
        </div>
        <div class="detail-item">
          <span class="label">Expected Return (Annualized):</span>
          <span class="value">{{ strategy.expectedReturn }}%</span>
        </div>
      </div>

      <section class="performance-section">
        <h2>Performance Metrics</h2>
        <p><em>(Historical performance data would be displayed here)</em></p>
        <!-- Placeholder for charts or tables -->
      </section>

      <section class="investment-details-section" v-if="userInvestment">
        <h2>Your Investment</h2>
        <div class="details-grid">
          <div class="detail-item">
            <span class="label">Amount Invested:</span>
            <span class="value">{{ formatCurrency(userInvestment.investedAmount) }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Current Value:</span>
            <span class="value">{{ formatCurrency(userInvestment.currentValue) }}</span>
          </div>
          <div class="detail-item">
            <span class="label">Profit/Loss:</span>
            <span class="value" :class="pnlClass(userInvestment.pnl)">{{ formatCurrency(userInvestment.pnl) }}</span>
          </div>
           <div class="detail-item">
            <span class="label">Investment Date:</span>
            <span class="value">{{ userInvestment.date }}</span>
          </div>
        </div>
      </section>

      <div class="actions">
        <button v-if="!isInvested" @click="investInStrategy" class="btn btn-primary">Invest in this Strategy</button>
        <button v-if="isInvested" @click="modifyInvestment" class="btn btn-secondary">Modify Investment</button>
        <NuxtLink to="/strategies" class="btn btn-outline">Back to All Strategies</NuxtLink>
      </div>

    </div>
    <div v-else>
      <p>Loading strategy details or strategy not found...</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const strategyId = computed(() => route.params.id as string);

interface Strategy {
  id: string;
  name: string;
  description: string;
  riskLevel: 'High' | 'Medium-High' | 'Medium' | 'Low';
  assetClass: string;
  minInvestment: number;
  expectedReturn: string; // Can be a range like "15-25"
}

interface UserInvestment {
  investedAmount: number;
  currentValue: number;
  pnl: number;
  date: string;
}

// --- Mock Data ---
// In a real application, this data would be fetched from an API based on strategyId.value
const allStrategiesData: Record<string, Strategy> = {
  'strategy001': {
    id: 'strategy001',
    name: 'Aggressive Growth Alpha',
    description: 'Aims for high capital appreciation by investing in volatile growth stocks and derivatives. Suitable for investors with a high risk tolerance.',
    riskLevel: 'High',
    assetClass: 'Equities, Derivatives',
    minInvestment: 5000,
    expectedReturn: '15-25'
  },
  'strategy002': {
    id: 'strategy002',
    name: 'Stable Income Beta',
    description: 'Focuses on generating consistent income through investments in bonds, dividend stocks, and REITs. Lower risk profile.',
    riskLevel: 'Low',
    assetClass: 'Fixed Income, Equities (Dividend)',
    minInvestment: 10000,
    expectedReturn: '4-7'
  },
  'strategy003': {
    id: 'strategy003',
    name: 'Tech Opportunities Gamma',
    description: 'Invests in a diversified portfolio of technology companies, from established leaders to emerging innovators.',
    riskLevel: 'Medium-High',
    assetClass: 'Equities (Technology Sector)',
    minInvestment: 7500,
    expectedReturn: '10-18'
  },
  'strategy004': {
    id: 'strategy004',
    name: 'Global Diversified Delta',
    description: 'Offers broad diversification across global equity and bond markets to balance risk and reward.',
    riskLevel: 'Medium',
    assetClass: 'Global Equities, Global Bonds',
    minInvestment: 12000,
    expectedReturn: '7-12'
  }
};

// Mock data for user's investment in this specific strategy
const userInvestmentsData: Record<string, UserInvestment> = {
    'strategy001': { investedAmount: 25000, currentValue: 27500, pnl: 2500, date: '2023-01-15' },
    'strategy002': { investedAmount: 30000, currentValue: 31500.75, pnl: 1500.75, date: '2022-11-20' },
};
// --- End Mock Data ---

const strategy = ref<Strategy | null>(null);
const userInvestment = ref<UserInvestment | null>(null);

const isInvested = computed(() => !!userInvestment.value);

onMounted(() => {
  // Simulate API call
  setTimeout(() => {
    strategy.value = allStrategiesData[strategyId.value] || null;
    userInvestment.value = userInvestmentsData[strategyId.value] || null;
  }, 200);
});

const formatCurrency = (value: number) => {
  if (typeof value !== 'number') return 'N/A';
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
};

const pnlClass = (pnl: number) => {
  if (typeof pnl !== 'number') return 'pnl-neutral';
  if (pnl > 0) return 'pnl-positive';
  if (pnl < 0) return 'pnl-negative';
  return 'pnl-neutral';
};

const investInStrategy = () => {
  alert(`Investing in ${strategy.value?.name}... (Placeholder)`);
  // API call to invest
};

const modifyInvestment = () => {
  alert(`Modifying investment in ${strategy.value?.name}... (Placeholder)`);
  // Navigate to a modification page or open a modal
};

definePageMeta({
  layout: 'default'
});
</script>

<style scoped>
.page-container {
  padding: 30px;
  background-color: #ffffff;
  border-radius: 8px;
  margin: 20px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

h1 {
  font-size: 2.2em;
  color: #1A237E; /* Deep Indigo */
  margin-bottom: 10px;
}

.strategy-description {
  font-size: 1.1em;
  color: #555;
  margin-bottom: 25px;
  line-height: 1.6;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.detail-item {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 6px;
  border: 1px solid #e8e8e8;
}

.detail-item .label {
  display: block;
  font-size: 0.9em;
  color: #666;
  margin-bottom: 5px;
  font-weight: 500;
}

.detail-item .value {
  font-size: 1.1em;
  font-weight: bold;
  color: #333;
}

.performance-section, .investment-details-section {
  margin-bottom: 30px;
}

.performance-section h2, .investment-details-section h2 {
  font-size: 1.6em;
  color: #283593; /* Indigo */
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.pnl-positive { color: #2E7D32; }
.pnl-negative { color: #C62828; }
.pnl-neutral { color: #555; }

.actions {
  margin-top: 30px;
  display: flex;
  gap: 15px;
  align-items: center;
}

.btn {
  padding: 10px 20px;
  border-radius: 5px;
  text-decoration: none;
  font-size: 1em;
  cursor: pointer;
  transition: background-color 0.2s ease, border-color 0.2s ease;
  border: 1px solid transparent;
}

.btn-primary {
  background-color: #FFC107; /* Amber */
  color: #333;
  font-weight: bold;
}
.btn-primary:hover {
  background-color: #FFB300; /* Darker Amber */
}

.btn-secondary {
  background-color: #3949AB; /* Indigo */
  color: white;
}
.btn-secondary:hover {
  background-color: #283593;
}

.btn-outline {
  background-color: transparent;
  border-color: #3949AB;
  color: #3949AB;
}
.btn-outline:hover {
  background-color: #e8eaf6; /* Light Indigo */
}
</style>