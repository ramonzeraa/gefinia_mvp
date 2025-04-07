import { createApp } from 'vue'
import App from './App.vue'
import router from './router';
import Navbar from './components/Navbar.vue';
import vue3GoogleLogin from 'vue3-google-login';

const app = createApp(App);
app.component('Navbar', Navbar);
app.use(router);
app.use(vue3GoogleLogin, {
  clientId: GOOGLE_CLIENT_ID,
});
app.mount('#app');