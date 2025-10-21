import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()], // O el que uses
    server: {
    proxy: {
      // Cualquier petición que empiece con /api...
        '/api': {
        // ...envíala a tu backend de Python
        target: 'http://localhost:8000',
        
        // Necesario para que el backend acepte la petición
        changeOrigin: true,
        
        // Reescribe la ruta: quita /api para que FastAPI la entienda
        // (ej. /api/lr1/build -> /lr1/build)
        rewrite: (path) => path.replace(/^\/api/, ''),
        } ,
    }
    }
})