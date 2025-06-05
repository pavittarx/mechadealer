type UserResponse = {
  is_error: boolean;
  message: string;
  is_success: boolean;
  data: {
    username: string;

    name: string;
    email: string;
    is_active: boolean;
    is_verified: boolean;
    capital: number;
    capital_remaining: number;
    capital_used: number;
  };
};

export const useUserStore = defineStore("userStore", {
  state: () => ({
    userId: -1,
    token: "",
    username: "",
    name: "",
    email: "",
    is_active: false,
    is_verified: false,
    capital: 0,
    capital_remaining: 0,
    capital_used: 0,
  }),
  actions: {
    setUserId(userId: number) {
      this.userId = userId;
    },
    setToken(token: string) {
      this.token = token;
    },
    async fetchUser() {
      if (!this.userId) {
        console.error("Unable to fetch user, UserId not present.");
        return;
      }

      const runtimeConfig = useRuntimeConfig();
      const baseUrl = runtimeConfig.public.baseUrl;

      try {
        const url = baseUrl + "/user/" + this.userId;
        const res: UserResponse = await $fetch(url, {
          method: "GET",
          headers: {
            Authorization: `Bearer ${this.token}`,
          },
        });

        if (res.is_error) {
          throw new Error(res.message || "Error fetching user data");
        }

        console.log("Fetched", res.data);

        this.username = res.data.username;
        this.name = res.data.name;
        this.email = res.data.email;
        this.is_active = res.data.is_active;
        this.is_verified = res.data.is_verified;
        this.capital = res.data.capital;
        this.capital_remaining = res.data.capital_remaining;
        this.capital_used = res.data.capital_used;
        console.log("User data fetched successfully:", res);
      } catch (error) {
        console.error("Error fetching user:", error);
      }
    },
    async fetchUserStrategies() {
      if (!this.userId) {
        console.error("Unable to fetch user holdings, UserId not present.");
        return;
      }

      const runtimeConfig = useRuntimeConfig();
      const baseUrl = runtimeConfig.public.baseUrl;

      try {
        const url = baseUrl + "/user/strategies/";
        const res: any = await $fetch(url, {
          method: "GET",
          headers: {
            Authorization: `Bearer ${this.token}`,
          },
        });

        if (res.is_error) {
          throw new Error(res.message || "Error fetching user holdings");
        }

        console.log("Fetched holdings", res.data);
        return res.data;
      } catch (error) {
        console.error("Error fetching user holdings:", error);
      }
    },
  },

  persist: {
    storage: import.meta.client && localStorage ? localStorage : undefined,
    pick: ["userId", "token"],
  },
});
