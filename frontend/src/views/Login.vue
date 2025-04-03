<template>
    <div class="login-container">
      <h1>Login</h1>
      <form @submit.prevent="handleLogin">
        <div>
          <label for="email">Email:</label>
          <input v-model="email" type="email" id="email" required />
        </div>
        <div>
          <label for="password">Senha:</label>
          <input v-model="password" type="password" id="password" required />
        </div>
        <button type="submit">Entrar</button>
      </form>
      <p>Não tem conta? <router-link to="/register">Cadastre-se</router-link></p>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        email: '',
        password: ''
      };
    },
    methods: {
      async handleLogin() {
        try {
          const response = await axios.post('http://localhost:5000/api/login', {
            email: this.email,
            password: this.password
          });
          const { user, token } = response.data;
          console.log('Token recebido:', token);
          localStorage.setItem('token', token);
          localStorage.setItem('user', JSON.stringify(user));
          console.log('Token armazenado no localStorage:', localStorage.getItem('token'));
          this.$router.push(`/profile/${user.id}`);
        } catch (error) {
          console.error('Erro ao fazer login:', error);
          alert('Email ou senha inválidos');
        }
      }
    }
  };
  </script>
  
  <style scoped>
  .login-container {
    max-width: 400px;
    margin: 0 auto;
    padding: 20px;
    background-color: #f9f9f9;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    text-align: center;
  }
  
  h1 {
    color: #2c3e50;
    margin-bottom: 20px;
  }
  
  form div {
    margin-bottom: 15px;
  }
  
  label {
    display: block;
    margin-bottom: 5px;
    color: #34495e;
  }
  
  input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  
  button {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    cursor: pointer;
    border-radius: 5px;
  }
  
  button:hover {
    background-color: #2980b9;
  }
  
  a {
    color: #3498db;
    text-decoration: none;
  }
  
  a:hover {
    text-decoration: underline;
  }
  </style>