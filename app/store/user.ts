export const useUserStore = defineStore("userStore", {
  state: () => ({
    id: -1,
    token: "",
  }),
  actions: {
    setUserId(userId: number) {
      this.id = userId;
    },
    setToken(token: string) {
      this.token = token;
    },
  },
});
