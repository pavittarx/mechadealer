type StrategiesData = {
  id: number;
  name: string;
  pnl: number;
  units: number;
  unrealized_pnl: number;
  capital: number;
  capital_remaining: number;
  capital_used: number;
  description: string;
  is_active: boolean;
  created_at: string;
};

type StrategiesResponse = {
  is_error: boolean;
  message: string;
  is_success: boolean;
  data: StrategiesData[];
};

// Pinia keys stores by this id. It read "userStore", the same id the user
// store registers, so both composables resolved to one store and the
// catalogue rendered the user's own positions instead of every strategy.
export const useStrategiesStore = defineStore("strategiesStore", {
  state: () => ({
    strategies: [] as StrategiesData[],
  }),
  actions: {
    async fetchStrategies() {
      const runtimeConfig = useRuntimeConfig();
      const baseUrl = runtimeConfig.public.baseUrl;

      try {
        const url = baseUrl + "/strategies";
        const res: StrategiesResponse = await $fetch(url, {
          method: "GET",
        });

        if (res.is_error) {
          throw new Error(res.message || "Error fetching user data");
        }

        this.strategies = res.data;
      } catch (error) {
        console.error("Error fetching user:", error);
      }
    },
  },
  persist: {
    storage: import.meta.client && localStorage ? localStorage : undefined,
    pick: ["strategies"],
  },
});
