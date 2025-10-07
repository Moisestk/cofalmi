// Mostrar toast al hacer clic en el botón "deshabilitado"
$(document).on('click', '.agregar-familia-btn.no-mas-familias', function(e) {
    e.preventDefault();
    mostrarToast(
        'Ya no puedes agregar más familias a esta casa. Si necesitas agregar más, edita la cantidad de familias permitidas.',
        true
    );
});



function mostrarToast(message, status = 'success') {
    const toastConfig = {
        success: { clase: 'text-bg-success', icono: 'fa fa-check-circle' },
        danger: { clase: 'text-bg-danger', icono: 'fa fa-times-circle' },
        warning: { clase: 'text-bg-warning', icono: 'fa fa-exclamation-triangle' },
        info: { clase: 'text-bg-info', icono: 'fa fa-info-circle' }
    };
    const config = toastConfig[status] || toastConfig.info;
    const toastHTML = `
        <div class="toast align-items-center ${config.clase} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="${config.icono} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    const newToast = $(toastHTML);
    $('#toast-container').append(newToast);
    const toast = new bootstrap.Toast(newToast, { delay: 5000 });
    toast.show();
    newToast.on('hidden.bs.toast', function () { $(this).remove(); });
}
// --- FIN: Función Toast ---

// --- INICIO: Bloque CSRF ---
// Función para obtener el token CSRF de las cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
// --- FIN: Bloque CSRF ---

$(document).ready(function() {

    // --- MANEJO DEL MODAL PARA AGREGAR FAMILIA ---
    // (Si tienes un modal para agregar familias en esta página, este código lo manejará)
    $(document).on('submit', '[id^="formAgregarFamilia"]', function(e) {
        e.preventDefault();

        var form = $(this);
        var url = form.attr('action');
        var data = form.serialize();
        var casaId = form.attr('id').replace('formAgregarFamilia', '');

        $.post(url, data)
            .done(function(response) {
                if (response.status === 'success') {
                    mostrarToast(response.message, 'success');
                    $('#modalAgregarFamilia' + casaId).modal('hide');
                    form[0].reset();
                    // Opcional: Si necesitas recargar o actualizar algo tras agregar.
                    // location.reload(); 
                }
            })
            .fail(function(xhr) {
                mostrarToast('Error al registrar la familia. Revise los datos.', 'danger');
            });
    });
   // --- MANEJO DEL MODAL PARA EDITAR FAMILIA ---

    // 1. Evento para RELLENAR el modal cuando se hace clic en un botón de editar
    $(document).on('click', '.btn-editar-familia', function(e) {
        e.preventDefault();

        var button = $(this);
        var familiaId = button.data('id');
        var nombre = button.data('nombre');
        var jefe = button.data('jefe');
        var telefono = button.data('telefono');
        var cantidad = button.data('cantidad');

        var url = `/familia/${familiaId}/editar/`;
        var modal = $('#modalEditarFamilia');

        // Rellenamos el formulario del modal
        modal.find('#edit_nombre_familia').val(nombre);
        modal.find('#edit_jefe_familia').val(jefe);
        modal.find('#edit_telefono_contacto').val(telefono);
        modal.find('#edit_cantidad_personas').val(cantidad);

        // Establecemos el 'action' del formulario
        modal.find('form').attr('action', url);

    }); // <-- Agrega este cierre para el evento click

// 2. Evento para ENVIAR el formulario de edición
$('#formEditarFamilia').on('submit', function(e) {
    e.preventDefault();

    var form = $(this);
    var url = form.attr('action');
    var data = form.serialize();

    $.post(url, data)
        .done(function(response) {
            if (response.status === 'success') {
                var table = $('#tabla-familias').DataTable();
                var familiaId = response.familia.id;
                var fila = table.row(`#familia-fila-${familiaId}`);

                if (fila.length) {
                    // Actualizamos los datos de la tabla (esto ya lo tenías bien)
                    fila.data([
                        fila.data()[0], // #
                        response.familia.nombre_familia,
                        response.familia.jefe_familia,
                        response.familia.telefono_contacto,
                        response.familia.cantidad_personas,
                        fila.data()[5] // Acciones
                    ]).draw(false);

                    // --- ¡NUEVO! Actualizamos los atributos data-* del botón ---
                    // Buscamos el botón de editar dentro de la fila que acabamos de actualizar
                    var botonEditar = fila.node().querySelector('.btn-editar-familia');
                    if (botonEditar) {
                        $(botonEditar).data('nombre', response.familia.nombre_familia);
                        $(botonEditar).data('jefe', response.familia.jefe_familia);
                        $(botonEditar).data('telefono', response.familia.telefono_contacto);
                        $(botonEditar).data('cantidad', response.familia.cantidad_personas);
                    }
                }
                
                // Primero ocultamos el modal
                $('#modalEditarFamilia').modal('hide');
                
                // Y LUEGO mostramos el toast. Esto evita conflictos.
                mostrarToast(response.message, 'success');
            }
        })
        .fail(function(xhr) {
            mostrarToast('Error al actualizar la familia. Revise los datos.', 'danger');
        });
    });
});

    // --- NUEVO: Manejo del envío del formulario para ELIMINAR familia ---
    $(document).on('submit', '[id^="formEliminarFamilia"]', function(e) {
        e.preventDefault(); // Evitamos que la página se recargue

        var form = $(this);
        var url = form.attr('action');

        $.post(url, form.serialize())
            .done(function(response) {
                if (response.status === 'success') {
                    var familiaId = response.familia_id;
                    
                    // 1. Cierra el modal de confirmación
                    $('#modalBorrarFamilia' + familiaId).modal('hide');
                    
                    // 2. Muestra el toast de éxito
                    mostrarToast(response.message, 'success');
                    
                    // 3. Elimina la fila de la tabla de familias
                    var tablaFamilias = $('#tabla-familias').DataTable();
                    tablaFamilias.row(`#familia-fila-${familiaId}`).remove().draw(false);
                    
                    // 4. (Opcional) Si necesitas actualizar el contador en la página anterior (lista de casas)
                    //    Este código buscará la tabla de casas y actualizará el contador allí.
                    var tablaCasas = $('#tabla-casas').DataTable();
                    if (tablaCasas.length) {
                        var filaCasa = tablaCasas.row(`tr[data-casa-id="${response.casa_id}"]`);
                        if(filaCasa.length) {
                            tablaCasas.cell(filaCasa, 2).data(response.nuevo_conteo_familias).draw(false);
                        }
                    }
                }
            })
            .fail(function(xhr) {
                mostrarToast('Error al eliminar la familia.', 'danger');
            });
    });

    
// --- FIN: Manejo del modal para eliminar familia ---