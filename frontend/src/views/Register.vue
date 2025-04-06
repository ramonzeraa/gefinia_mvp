<template>
  <navbar />
    <div class="login-container">
      <h1>Cadastro</h1>
      <form @submit.prevent="handleRegister">
        <div>
          <label for="name">Nome:</label>
          <input v-model="name" type="text" id="name" required />
        </div>
        <div>
          <label for="email">Email:</label>
          <input v-model="email" type="email" id="email" required />
        </div>
        <div>
          <label for="password">Senha:</label>
          <input v-model="password" type="password" id="password" required />
        </div>
        <button type="submit">Cadastrar</button>
      </form>
      <p>Já tem conta? <router-link to="/login">Faça login</router-link></p>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    data() {
      return {
        name: '',
        email: '',
        password: ''
      };
    },
    methods: {
      async handleRegister() {
        try {
          const response = await axios.post('http://localhost:5000/api/register', {
            name: this.name,
            email: this.email,
            password: this.password
          });
          console.log('Usuário registrado com sucesso', response.data);
          alert('Usuário registrado com sucesso! Faça login para continuar.');
          this.$router.push('/login');
        } catch (error) {
          console.error('Erro ao cadastrar:', error);
          if (error.response && error.response.status === 409) {
            alert('Email já registrado. Tente outro email.');
          } else { 
            alert('Erro ao cadastrar:' + (error.response?.data?.error || 'Erro desconhecido'));
          }
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