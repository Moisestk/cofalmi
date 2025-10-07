// JavaScript simplificado para toggles de contraseña
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando toggles de contraseña simplificados...');
    
    // Función simple para toggle de contraseña
    function togglePassword(button) {
        console.log('👁️ Toggle clickeado');
        
        const inputGroup = button.closest('.input-group');
        const input = inputGroup ? inputGroup.querySelector('input') : null;
        const icon = button.querySelector('i');
        
        if (!input || !icon) {
            console.error('❌ Input o icono no encontrado');
            return;
        }
        
        console.log(`Estado inicial: input.type = "${input.type}"`);
        
        // Toggle simple
        if (input.type === 'password') {
            input.type = 'text';
            icon.className = 'fas fa-eye';
            console.log('✅ Contraseña VISIBLE');
        } else {
            input.type = 'password';
            icon.className = 'fas fa-eye-slash';
            console.log('🔒 Contraseña OCULTA');
        }
    }
    
    // Inicializar todos los toggles
    function initializeToggles() {
        const toggles = document.querySelectorAll('.show-password-toggle');
        console.log(`📊 Encontrados ${toggles.length} toggles`);
        
        toggles.forEach((toggle, index) => {
            // Asegurar estado inicial
            const inputGroup = toggle.closest('.input-group');
            const input = inputGroup ? inputGroup.querySelector('input') : null;
            const icon = toggle.querySelector('i');
            
            if (input && icon) {
                input.type = 'password';
                icon.className = 'fas fa-eye-slash';
                console.log(`✅ Toggle ${index + 1} inicializado`);
            }
            
            // Agregar event listener
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                togglePassword(this);
            });
        });
    }
    
    // Inicializar al cargar
    initializeToggles();
    
    // Función global para debug
    window.debugPasswordToggles = function() {
        console.log('🔍 === DEBUG TOGGLES ===');
        const toggles = document.querySelectorAll('.show-password-toggle');
        toggles.forEach((toggle, index) => {
            const inputGroup = toggle.closest('.input-group');
            const input = inputGroup ? inputGroup.querySelector('input') : null;
            const icon = toggle.querySelector('i');
            console.log(`Toggle ${index + 1}: input.type="${input ? input.type : 'NO'}", icon="${icon ? icon.className : 'NO'}"`);
        });
    };
    
    console.log('✅ Sistema de toggles inicializado');
});
