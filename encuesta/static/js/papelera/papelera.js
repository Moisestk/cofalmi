    $(document).ready(function() {
        // Función para mostrar notificaciones (toasts)
        function showToast(message, type = 'success') {
            const toastContainer = document.getElementById('toast-container');
            if (!toastContainer) return;

            const toastId = 'toast-' + Date.now();
            const bgClass = type === 'success' ? 'text-bg-success' : 'text-bg-danger';
            const iconClass = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle';

            const toastHtml = `
                <div id="${toastId}" class="toast align-items-center ${bgClass} border-0" role="alert" aria-live="assertive" aria-atomic="true">
                    <div class="d-flex">
                        <div class="toast-body"><i class="fa ${iconClass} me-2"></i>${message}</div>
                        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button>
                    </div>
                </div>`;
            toastContainer.insertAdjacentHTML('beforeend', toastHtml);

            const toastEl = document.getElementById(toastId);
            const toast = new bootstrap.Toast(toastEl, { delay: 3500 });
            toast.show();
            toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
        }

        // Función para inicializar DataTables con opciones comunes
        function initializeDataTable(selector) {
            return $(selector).DataTable({
                responsive: true,
                language: {
                    lengthMenu: "Mostrar _MENU_ registros",
                    zeroRecords: "No se encontraron resultados",
                    info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
                    infoEmpty: "Mostrando 0 a 0 de 0 registros",
                    infoFiltered: "(filtrado de _MAX_ registros totales)",
                    search: "Buscar:",
                    paginate: {
                        first: "Primero",
                        last: "Último",
                        next: "Siguiente",
                        previous: "Anterior"
                    }
                }
            });
        }

        // Inicializa todas las tablas
        const dataTables = {
            comunidades: initializeDataTable('#tabla-comunidades-papelera'),
            encuestas: initializeDataTable('#tabla-encuestas-papelera'),
            encuestados: initializeDataTable('#tabla-encuestados-papelera')
        };
        
        // Mostrar/ocultar tablas según el filtro
        function mostrarTabla(tabla) {
            $('#tabla-comunidades-wrapper, #tabla-encuestas-wrapper, #tabla-encuestados-wrapper').hide();
            $(`#tabla-${tabla}-wrapper`).show();
        }

        // Inicialmente muestra comunidades
        mostrarTabla('comunidades');

        $('#papelera-filtro').on('change', function() {
            mostrarTabla($(this).val());
        });

    // --- EXPANDIBLE PARA NOMBRE LARGO EN MODALES ---
    function setNombreExpandible(spanId, toggleId, nombreCompleto) {
        const $nombre = $('#' + spanId);
        const $toggle = $('#' + toggleId);

        // Estado inicial: truncado
        $nombre.removeClass('nombre-expandido').addClass('nombre-truncado').text(nombreCompleto);
        $toggle.text('[ver más]');

        // Elimina handlers previos para evitar duplicados
        $toggle.off('click');
        $nombre.off('click');

        function expandir() {
            $nombre.removeClass('nombre-truncado').addClass('nombre-expandido');
            $toggle.text('[ver menos]');
        }
        function truncar() {
            $nombre.removeClass('nombre-expandido').addClass('nombre-truncado');
            $toggle.text('[ver más]');
        }

        // Alternar al hacer clic en el nombre o el botón
        $toggle.on('click', function() {
            if ($nombre.hasClass('nombre-truncado')) {
                expandir();
            } else {
                truncar();
            }
        });
        $nombre.on('click', function() {
            if ($nombre.hasClass('nombre-truncado')) {
                expandir();
            } else {
                truncar();
            }
        });
    }

    // --- MODAL ELIMINAR ---
    const confirmDeleteModal = document.getElementById('confirmDeleteModal');
    let formToSubmit = null;
    if (confirmDeleteModal) {
        confirmDeleteModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const itemName = button.getAttribute('data-item-name');
            formToSubmit = button.closest('form');
            setNombreExpandible('confirm-delete-item-name', 'toggle-delete-expand', itemName);
            $('#delete-password').val('');
            $('#delete-password-error').hide();
        });
        $('#confirmDeleteBtn').on('click', function () {
            const password = $('#delete-password').val();
            if (!password) {
                $('#delete-password-error').text('Debes ingresar la contraseña.').show();
                $('#delete-password').focus();
                return;
            }
            if (formToSubmit) {
                const form = $(formToSubmit);
                const row = form.closest('tr');
                const tableId = row.closest('table').attr('id');
                const tableKey = tableId.split('-')[1];
                const table = dataTables[tableKey];
                let formData = form.serializeArray();
                formData.push({name: 'password', value: password});
                $.ajax({
                    url: form.attr('action'),
                    type: 'POST',
                    data: $.param(formData),
                    success: function(response) {
                        $('#confirmDeleteModal').modal('hide');
                        table.row(row).remove().draw();
                        showToast('Elemento eliminado permanentemente.', 'success');
                    },
                    error: function(xhr) {
                        let msg = 'Error al eliminar el elemento.';
                        if (xhr.responseJSON && xhr.responseJSON.error) {
                            msg = xhr.responseJSON.error;
                        }
                        $('#delete-password-error').text(msg).show();
                    }
                });
            }
        });
    }

    // --- MODAL RESTAURAR ---
    const confirmRestoreModal = document.getElementById('confirmRestoreModal');
    let restoreFormToSubmit = null;
    if (confirmRestoreModal) {
        confirmRestoreModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            const itemName = button.getAttribute('data-item-name');
            restoreFormToSubmit = button.closest('form');
            setNombreExpandible('confirm-restore-item-name', 'toggle-restore-expand', itemName);
        });
        $('#confirmRestoreBtn').on('click', function () {
            if (restoreFormToSubmit) {
                const form = $(restoreFormToSubmit);
                const row = form.closest('tr');
                const tableId = row.closest('table').attr('id');
                const tableKey = tableId.split('-')[1];
                const table = dataTables[tableKey];
                $.ajax({
                    url: form.attr('action'),
                    type: 'POST',
                    data: form.serialize(),
                    success: function(response) {
                        $('#confirmRestoreModal').modal('hide');
                        table.row(row).remove().draw();
                        showToast('Elemento restaurado con éxito.', 'success');
                    },
                    error: function() {
                        $('#confirmRestoreModal').modal('hide');
                        showToast('Error al restaurar el elemento.', 'danger');
                    }
                });
            }
        });
    }

    // Manejar restauración con AJAX (por si acaso)
    $('body').on('submit', '.form-ajax-action', function(e) {
        e.preventDefault();
        // No hacer nada aquí, la restauración se maneja por el modal
    });
});
