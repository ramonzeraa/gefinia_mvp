<template>
    <div class="welcome-container">
      <Navbar />
      <h1>Bem-vindo ao GeFinIA</h1>
      <p>Gerencie suas finanças pessoais de forma simples e eficiente.</p>
      <div class="welcome-actions">
        <router-link v-if="user" to="/dashboard" class="btn">Ir para o Dashboard</router-link>
        <router-link v-else to="/login" class="btn">Fazer Login</router-link>
        <router-link v-else to="/register" class="btn btn-secondary">Cadastre-se</router-link>
      </div>
    </div>
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
    }
  };
  </script>
  
  <style scoped>
  .welcome-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 40px 20px;
    text-align: center;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
  
  h1 {
    color: #2c3e50;
    margin-bottom: 20px;
  }
  
  p {
    color: #34495e;
    font-size: 18px;
    margin-bottom: 30px;
  }
  
  .welcome-actions {
    display: flex;
    justify-content: center;
    gap: 15px;
  }
  
  .btn {
    background-color: #3498db;
    color: white;
    padding: 10px 20px;
    text-decoration: none;
    border-radius: 5px;
    transition: background-color 0.3s;
  }
  
  .btn:hover {
    background-color: #2980b9;
  }
  
  .btn-secondary {
    background-color: #7f8c8d;
  }
  
  .btn-secondary:hover {
    background-color: #6c757d;
  }
  </style>