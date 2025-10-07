document.addEventListener('DOMContentLoaded', function() {
    // Función para alternar la visibilidad de la contraseña
    const toggleButtons = document.querySelectorAll('.show-password-toggle');
    
    toggleButtons.forEach(button => {
        // Asegurar que el botón tenga color inicial
        button.style.color = '#6c757d';
        button.style.backgroundColor = '#f8f9fa';
        
        button.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
                this.classList.add('active');
                this.style.color = '#495057';
                this.style.backgroundColor = '#e9ecef';
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
                this.classList.remove('active');
                this.style.color = '#6c757d';
                this.style.backgroundColor = '#f8f9fa';
            }
        });
        
        // Mantener estilos durante hover y fuera de hover
        button.addEventListener('mouseenter', function() {
            if (!this.classList.contains('active')) {
                this.style.color = '#495057';
                this.style.backgroundColor = '#e9ecef';
            }
        });
        
        button.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                this.style.color = '#6c757d';
                this.style.backgroundColor = '#f8f9fa';
            }
        });
    });
    
    // Verificación de coincidencia de contraseñas
    const newPassword1 = document.getElementById('new_password1');
    const newPassword2 = document.getElementById('new_password2');
    const matchIndicator = document.getElementById('password-match');
    const strengthIndicator = document.getElementById('password-strength');
    
    if (newPassword1 && newPassword2 && matchIndicator) {
        newPassword2.addEventListener('input', function() {
            if (this.value.length === 0) {
                matchIndicator.textContent = '';
                matchIndicator.className = 'form-text mt-1';
            } else if (this.value !== newPassword1.value) {
                matchIndicator.textContent = 'Las contraseñas no coinciden';
                matchIndicator.className = 'form-text mt-1 text-danger';
            } else {
                matchIndicator.textContent = 'Las contraseñas coinciden';
                matchIndicator.className = 'form-text mt-1 text-success';
            }
        });
        
        // Verificación de fortaleza de contraseña
        newPassword1.addEventListener('input', function() {
            const password = this.value;
            
            if (password.length === 0) {
                strengthIndicator.textContent = '';
                strengthIndicator.className = 'form-text mt-1';
                return;
            }
            
            // Calcular fortaleza
            let strength = 0;
            if (password.length >= 8) strength++;
            if (/[A-Z]/.test(password)) strength++;
            if (/[0-9]/.test(password)) strength++;
            if (/[^A-Za-z0-9]/.test(password)) strength++;
            
            // Mostrar mensaje según fortaleza
            if (strength <= 1) {
                strengthIndicator.textContent = 'Contraseña débil';
                strengthIndicator.className = 'form-text mt-1 text-danger';
            } else if (strength <= 3) {
                strengthIndicator.textContent = 'Contraseña media';
                strengthIndicator.className = 'form-text mt-1 text-warning';
            } else {
                strengthIndicator.textContent = 'Contraseña fuerte';
                strengthIndicator.className = 'form-text mt-1 text-success';
            }
        });
    }
    
    // Inicializar todos los botones con estilos correctos
    function initializeToggleButtons() {
        const buttons = document.querySelectorAll('.show-password-toggle');
        buttons.forEach(button => {
            button.style.color = '#6c757d';
            button.style.backgroundColor = '#f8f9fa';
            button.style.borderColor = '#ced4da';
            button.style.borderLeft = 'none';
        });
    }
    
    initializeToggleButtons();
});