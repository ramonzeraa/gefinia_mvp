<template>
    <nav class="navbar">
      <div class="navbar-brand">
        <router-link to="/" class="navbar-logo">GeFinIA</router-link>
      </div>
      <div class="navbar-links">
        <router-link to="/dashboard" class="navbar-item">Dashboard</router-link>
        <router-link v-if="user" :to="'/profile/' + user.id" class="navbar-item">Perfil</router-link>
        <router-link v-else to="/login" class="navbar-item">Login</router-link>
        <router-link v-if="user" to="/login" class="navbar-item" @click.prevent="logout">Sair</router-link>
        <router-link v-else to="/register" class="navbar-item">Cadastre-se</router-link>
      </div>
    </nav>
  </template>
  
  <script>
  export default {
    data() {
      return {
        user: null
      };
    },
    mounted() {
      const userData = localStorage.getItem('user');
      if (userData) {
        this.user = JSON.parse(userData);
      }
    },
    methods: {
      logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        this.user = null;
        this.$router.push('/login');
      }
    }
  };
  </script>
  
  <style scoped>
  .navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background-color: #2c3e50;
    padding: 1rem;
    color: white;
  }
  
  .navbar-brand {
    font-size: 1.5rem;
    font-weight: bold;
  }
  
  .navbar-logo {
    color: white;
    text-decoration: none;
  }
  
  .navbar-links {
    display: flex;
    gap: 1rem;
  }
  
  .navbar-item {
    color: white;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    transition: background-color 0.3s;
  }
  
  .navbar-item:hover {
    background-color: #34495e;
  }
  </style>