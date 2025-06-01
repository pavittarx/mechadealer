export const useUserStore = defineStore("userStore", {
  state: () => ({
    userId: -1,
    token: "",
  }),
  actions: {
    setUserId(userId: number) {
      this.userId = userId;
    },
    setToken(token: string) {
      this.token = token;
    },
  },
  persist: {
    storage: process.client && localStorage ? localStorage : undefined,
    pick: ["userId", "token"],
  },
});
