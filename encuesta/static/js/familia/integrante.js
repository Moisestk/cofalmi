// en static/js/integrante.js

$(document).ready(function() {

    // --- FUNCIÓN PARA ACTUALIZAR EL CONTADOR Y EL BOTÓN ---
    function actualizarContadorIntegrante(modal) {
        const capacidad = parseInt(modal.data('capacidad'), 10) || 0;
        const actuales = parseInt(modal.data('actual'), 10) || 0;
        const formularios = modal.find('.integrante-form-seccion').length;
        const total = actuales + formularios;
        
        // Apunta al contador por su ID estático y actualiza el texto
        modal.find('#contador-integrantes').text(`(${total} / ${capacidad} personas)`);
        
        const btnAgregar = modal.find('.btn-agregar-otro-integrante');
        
        // Oculta el botón de agregar si se alcanza o supera la capacidad
        if (capacidad === 0 || total >= capacidad) {
            btnAgregar.hide();
        } else {
            btnAgregar.show();
        }
    }

    // --- EVENTO PARA CONFIGURAR EL MODAL AL HACER CLIC EN EL BOTÓN "AGREGAR INTEGRANTE" ---
    $(document).on('click', '.btn-agregar-integrante', function() {
        const button = $(this);
        const modal = $('#modalAgregarIntegrante');

        // Pasa los datos del botón al modal para que los almacene
        modal.data('familia-id', button.data('familia-id'));
        modal.data('capacidad', parseInt(button.data('capacidad'), 10) || 0);
        modal.data('actual', parseInt(button.data('actual'), 10) || 0);
        
        // Actualiza el título del modal con el nombre de la familia
        modal.find('.modal-title span').text(button.data('familia-nombre'));
        
        // Llama a la función para que muestre el contador inicial correcto
        actualizarContadorIntegrante(modal);
    });

    // --- EVENTO PARA CLONAR EL FORMULARIO ---
    $(document).on('click', '.btn-agregar-otro-integrante', function() {
        const modal = $(this).closest('.modal');
        const contenedor = modal.find('.contenedor-formularios-integrante');
        const template = contenedor.find('.integrante-form-seccion:first');
        const nuevoForm = template.clone();

        // Limpia todos los campos del nuevo formulario clonado
        nuevoForm.find('input, select, textarea').val('');
        nuevoForm.find('input[type="checkbox"]').prop('checked', false);

        const nuevoNumero = new Date().getTime(); // Crea un ID único para evitar conflictos
        const numeroIntegrante = contenedor.find('.integrante-form-seccion').length + 1;
        nuevoForm.find('h6.integrante-titulo').text(`Datos del Integrante ${numeroIntegrante}`);
        
        // Asigna IDs únicos al acordeón para que cada uno se abra y cierre independientemente
        nuevoForm.find('.accordion').attr('id', 'accordionSaludUnico_' + nuevoNumero);
        nuevoForm.find('.accordion-button').attr('data-bs-target', '#collapseSaludUnico_' + nuevoNumero).removeClass('collapsed');
        nuevoForm.find('.accordion-collapse').attr('id', 'collapseSaludUnico_' + nuevoNumero).removeClass('show');

        // Actualiza los IDs de los checkboxes de salud para evitar conflictos
        nuevoForm.find('#patologias-container-1').attr('id', 'patologias-container-' + nuevoNumero);
        nuevoForm.find('#medicamentos-container-1').attr('id', 'medicamentos-container-' + nuevoNumero);
        nuevoForm.find('#insumos-container-1').attr('id', 'insumos-container-' + nuevoNumero);

        // Actualiza los IDs de los checkboxes individuales
        nuevoForm.find('input[name="patologias"]').each(function() {
            const originalId = $(this).attr('id');
            const newId = originalId.replace('patologia_1_', 'patologia_' + nuevoNumero + '_');
            $(this).attr('id', newId);
            $(this).next('label').attr('for', newId);
        });

        nuevoForm.find('input[name="medicamentos"]').each(function() {
            const originalId = $(this).attr('id');
            const newId = originalId.replace('medicamento_1_', 'medicamento_' + nuevoNumero + '_');
            $(this).attr('id', newId);
            $(this).next('label').attr('for', newId);
        });

        nuevoForm.find('input[name="insumos"]').each(function() {
            const originalId = $(this).attr('id');
            const newId = originalId.replace('insumo_1_', 'insumo_' + nuevoNumero + '_');
            $(this).attr('id', newId);
            $(this).next('label').attr('for', newId);
        });

        // Crea y añade el botón para quitar el formulario
        const botonQuitar = $('<button type="button" class="btn btn-danger btn-sm btn-quitar-integrante" style="position: absolute; top: 10px; right: 10px;"><i class="fa fa-times"></i></button>');
        nuevoForm.css('position', 'relative').append(botonQuitar);
        
        contenedor.append(nuevoForm);
        actualizarContadorIntegrante(modal);
    });
    
    // --- EVENTO PARA QUITAR UN FORMULARIO ---
    $(document).on('click', '.btn-quitar-integrante', function() {
        const modal = $(this).closest('.modal');
        $(this).closest('.integrante-form-seccion').remove();
        actualizarContadorIntegrante(modal);
    });

    // --- EVENTO PARA GUARDAR TODOS LOS INTEGRANTES ---
    $(document).on('click', '.btn-guardar-integrantes', function(e) {
        e.preventDefault();
        const modal = $('#modalAgregarIntegrante');
        const familiaId = modal.data('familia-id');
        const url = `/familia/${familiaId}/agregar-integrante/`;
        const formSections = modal.find('.integrante-form-seccion');
        let promises = [];

        // Validar que al menos un formulario tenga datos básicos
        let formulariosValidos = 0;
        formSections.each(function() {
            const nombre = $(this).find('input[name="nombre"]').val().trim();
            const apellido = $(this).find('input[name="apellido"]').val().trim();
            const cedula = $(this).find('input[name="cedula_numero"]').val().trim();
            
            if (nombre && apellido && cedula) {
                formulariosValidos++;
            }
        });

        if (formulariosValidos === 0) {
            mostrarToast('Debe completar al menos un integrante con datos básicos.', 'warning');
            return;
        }

        formSections.each(function() {
            const nombre = $(this).find('input[name="nombre"]').val().trim();
            const apellido = $(this).find('input[name="apellido"]').val().trim();
            const cedula = $(this).find('input[name="cedula_numero"]').val().trim();
            
            // Solo procesar formularios con datos básicos
            if (nombre && apellido && cedula) {
                const formData = new FormData();
                
                // Datos básicos del integrante
                formData.append('nombre', nombre);
                formData.append('apellido', apellido);
                formData.append('tipo_cedula', $(this).find('select[name="tipo_cedula"]').val());
                formData.append('cedula_numero', cedula);
                formData.append('genero', $(this).find('select[name="genero"]').val());
                
                // Datos de salud
                const patologias = [];
                $(this).find('input[name="patologias"]:checked').each(function() {
                    patologias.push($(this).val());
                });
                formData.append('patologias', patologias.join(','));
                formData.append('otros_patologias', $(this).find('textarea[name="otros_patologias"]').val());
                
                const medicamentos = [];
                $(this).find('input[name="medicamentos"]:checked').each(function() {
                    medicamentos.push($(this).val());
                });
                formData.append('medicamentos', medicamentos.join(','));
                formData.append('otros_medicamentos', $(this).find('textarea[name="otros_medicamentos"]').val());
                
                const insumos = [];
                $(this).find('input[name="insumos"]:checked').each(function() {
                    insumos.push($(this).val());
                });
                formData.append('insumos', insumos.join(','));
                formData.append('otros_insumos', $(this).find('textarea[name="otros_insumos"]').val());
                
                // Agregar CSRF token
                formData.append('csrfmiddlewaretoken', $('input[name="csrfmiddlewaretoken"]').val());
                
                promises.push($.ajax({
                    url: url,
                    type: 'POST',
                    data: formData,
                    processData: false,
                    contentType: false
                }));
            }
        });

        // Espera a que todas las peticiones AJAX terminen
        $.when.apply($, promises).done(function() {
            modal.modal('hide');
            mostrarToast(`Se agregaron ${promises.length} integrante(s) correctamente.`, 'success');
            location.reload(); 
        }).fail(function(xhr) {
            console.error('Error al guardar integrantes:', xhr);
            mostrarToast('Ocurrió un error al guardar uno o más integrantes.', 'danger');
        });
    });

    // --- EVENTO AL CERRAR EL MODAL ---
    // Resetea el modal a su estado original (1 solo formulario) para la próxima vez
    $('#modalAgregarIntegrante').on('hidden.bs.modal', function () {
        const modal = $(this);
        // Elimina todos los formularios clonados, dejando solo el primero
        modal.find('.integrante-form-seccion:not(:first)').remove();
        
        // Limpia todos los campos del primer formulario
        const firstForm = modal.find('.integrante-form-seccion:first');
        firstForm.find('input, select, textarea').val('');
        firstForm.find('input[type="checkbox"]').prop('checked', false);
        firstForm.find('h6.integrante-titulo').text('Datos del Integrante 1');
        firstForm.find('.accordion-collapse').removeClass('show');
    });
});