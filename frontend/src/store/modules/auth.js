// src/store/modules/auth.js
import axios from 'axios'

const state = {
  user: null
}

const getters = {
  getUser: state => state.user
}

const mutations = {
  SET_USER(state, user) {
    state.user = user
  }
}

const actions = {
  async fetchUser({ commit }, userId) {
    try {
      const response = await axios.get(`/api/users/${userId}/`)
      commit('SET_USER', response.data)
    } catch (error) {
      console.error(error)
    }
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}