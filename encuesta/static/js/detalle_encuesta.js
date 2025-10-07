$(document).ready(function() {
    // Utilidades para obtener URLs y CSRF
    const urls = window.DETALLE_ENCUESTA_URLS;

    function crearInputOpcion(valor = '') {
        return `<div class="input-group mb-1 opcion-item">
            <input type="text" name="opciones[]" class="form-control opcion-input" value="${valor}" placeholder="Opción" required>
            <button type="button" class="btn btn-outline-danger btn-sm btnQuitarOpcion" tabindex="-1" title="Quitar opción">
                <i class="fa fa-times"></i>
            </button>
        </div>`;
    }

    function actualizarVistaPrevia() {
        let tipo = $('#tipo_respuesta').val();
        let opciones = [];
        $('.opcion-input').each(function() {
            let val = $(this).val().trim();
            if (val !== '') opciones.push(val);
        });
        let preview = '';

        if (tipo === 'opcion_unica') {
            if (opciones.length === 0) {
                preview = `<div class="text-muted">Agrega opciones para previsualizar</div>`;
            } else {
                preview = opciones.map(op =>
                    `<div class="form-check mb-2">
                        <input class="form-check-input pointer-events-none" type="radio" tabindex="-1">
                        <label class="form-check-label text-dark">${op}</label>
                    </div>`
                ).join('');
            }
        } else if (tipo === 'opcion_multiple') {
            if (opciones.length === 0) {
                preview = `<div class="text-muted">Agrega opciones para previsualizar</div>`;
            } else {
                preview = opciones.map(op =>
                    `<div class="form-check mb-2">
                        <input class="form-check-input pointer-events-none" type="checkbox" tabindex="-1">
                        <label class="form-check-label text-dark">${op}</label>
                    </div>`
                ).join('');
            }
        } else if (tipo === 'si_no') {
            preview = `<div class="form-check mb-2">
                            <input class="form-check-input pointer-events-none" type="radio" tabindex="-1">
                            <label class="form-check-label text-dark">Sí</label>
                        </div>
                        <div class="form-check mb-2">
                            <input class="form-check-input pointer-events-none" type="radio" tabindex="-1">
                            <label class="form-check-label text-dark">No</label>
                        </div>`;
        } else {
            preview = '<div class="text-muted">Seleccione primero el tipo de pregunta y respuesta.</div>';
        }
        $('#previewPregunta').html(preview);
    }

    $('#tipo_respuesta').on('change', function() {
        let tipo = $(this).val();
        $('#opciones_inputs').empty();
        if (tipo === 'opcion_unica' || tipo === 'opcion_multiple') {
            $('#opciones_group').show();
            $('#campo_texto_group').hide();
            $('#opciones_inputs').append(crearInputOpcion());
            $('#opciones_inputs').append(crearInputOpcion());
        } else if (tipo === 'si_no') {
            $('#opciones_group').hide();
            $('#campo_texto_group').show();
        } else {
            $('#opciones_group').hide();
            $('#campo_texto_group').hide();
        }
        actualizarVistaPrevia();
    });

    // Mostrar/ocultar campo de título cuando se marca el checkbox
    $('#requiere_campo_texto').on('change', function() {
        if ($(this).is(':checked')) {
            $('#titulo_campo_texto_group').show();
            $('#titulo_campo_texto').val('Indique cuál');
        } else {
            $('#titulo_campo_texto_group').hide();
            $('#titulo_campo_texto').val('');
        }
    });

    // Para el modal de editar
    $('#editar_requiere_campo_texto').on('change', function() {
        if ($(this).is(':checked')) {
            $('#editar_titulo_campo_texto_group').show();
            if (!$('#editar_titulo_campo_texto').val()) {
                $('#editar_titulo_campo_texto').val('Indique cuál');
            }
        } else {
            $('#editar_titulo_campo_texto_group').hide();
            $('#editar_titulo_campo_texto').val('');
        }
    });

    $('#btnAgregarOpcion').on('click', function() {
        $('#opciones_inputs').append(crearInputOpcion());
        actualizarVistaPrevia();
    });

    $('#opciones_inputs').on('click', '.btnQuitarOpcion', function() {
        $(this).closest('.opcion-item').remove();
        actualizarVistaPrevia();
    });

    $('#opciones_inputs').on('input', '.opcion-input', actualizarVistaPrevia);

    $('#modalPregunta').on('shown.bs.modal', function () {
        actualizarVistaPrevia();
    });

    $('#btnLimpiar').on('click', function() {
        $('#formNuevaPregunta')[0].reset();
        $('#opciones_group').hide();
        $('#campo_texto_group').hide();
        $('#opciones_inputs').empty();
        actualizarVistaPrevia();
    });

    // Validación para nueva pregunta
    $('#formNuevaPregunta').on('submit', function(e) {
        let tipo = $('#tipo_respuesta').val();
        if (tipo === 'opcion_unica' || tipo === 'opcion_multiple') {
            let opciones = [];
            $('.opcion-input').each(function() {
                let val = $(this).val().trim();
                if (val !== '') opciones.push(val);
            });
            if (opciones.length < 2) {
                alert('Debes agregar al menos dos opciones.');
                e.preventDefault();
                return false;
            }
        }
        e.preventDefault();
        let form = $(this);
        $.ajax({
            url: urls.agregar_pregunta,
            type: "POST",
            data: form.serialize(),
            headers: {'X-CSRFToken': urls.csrf_token},
            success: function(response) {
                $('#modalPregunta').modal('hide');
                location.reload();
            },
            error: function(xhr) {
                alert('Ocurrió un error al guardar la pregunta.');
            }
        });
    });

    // Abrir modal y cargar el id/texto para eliminar
    $(document).on('click', '.btnEliminarPregunta', function() {
        var preguntaId = $(this).data('pregunta-id');
        var texto = $(this).data('texto');
        $('#modal-eliminar-texto').text(texto);
        $('#inputEliminarPreguntaId').val(preguntaId);
        $('#modalEliminarPregunta').modal('show');
    });

    // Eliminar pregunta (submit)
    $(document).on('submit', '#formEliminarPregunta', function(e) {
        e.preventDefault();
        let preguntaId = $('#inputEliminarPreguntaId').val();
        $.ajax({
            url: urls.eliminar_pregunta,
            type: "POST",
            data: {
                pregunta_id: preguntaId,
                csrfmiddlewaretoken: urls.csrf_token
            },
            success: function(response) {
                if (response.ok) {
                    $('#modalEliminarPregunta').modal('hide');
                    location.reload();
                }
            }
        });
    });

    // Abrir modal y cargar datos del editar pregunta
    $(document).on('click', '.btnEditarPregunta', function() {
        let preguntaId = $(this).data('pregunta-id');
        $.get(urls.obtener_pregunta, {pregunta_id: preguntaId}, function(data) {
            $('#editar_pregunta_id').val(data.id);
            $('#editar_texto_pregunta').val(data.texto_pregunta);
            $('#editar_tipo_respuesta').val(data.tipo_respuesta);
            $('#editar_opciones_inputs').empty();
            
            // Manejar campo de texto adicional
            if (data.tipo_respuesta === 'si_no') {
                $('#editar_campo_texto_group').show();
                if (data.titulo_campo_texto) {
                    $('#editar_requiere_campo_texto').prop('checked', true);
                    $('#editar_titulo_campo_texto').val(data.titulo_campo_texto);
                    $('#editar_titulo_campo_texto_group').show();
                } else {
                    $('#editar_requiere_campo_texto').prop('checked', false);
                    $('#editar_titulo_campo_texto_group').hide();
                }
            } else {
                $('#editar_campo_texto_group').hide();
            }
            
            if (data.tipo_respuesta === 'opcion_unica' || data.tipo_respuesta === 'opcion_multiple') {
                $('#editar_opciones_group').show();
                data.opciones.forEach(function(opcion) {
                    $('#editar_opciones_inputs').append(
                        `<div class="input-group mb-1 editar-opcion-item">
                            <input type="text" name="opciones[]" class="form-control editar-opcion-input" value="${opcion.texto_opcion}" data-opcion-id="${opcion.id}" required>
                            <button type="button" class="btn btn-outline-danger btn-sm btnEditarQuitarOpcion" data-opcion-id="${opcion.id}" tabindex="-1" title="Quitar opción">
                                <i class="fa fa-times"></i>
                            </button>
                        </div>`
                    );
                });
            } else {
                $('#editar_opciones_group').hide();
            }
            $('#modalEditarPregunta').modal('show');
        });
    });

    // Cambiar tipo de respuesta en edición
    $('#editar_tipo_respuesta').on('change', function() {
        let tipo = $(this).val();
        $('#editar_opciones_inputs').empty();
        if (tipo === 'opcion_unica' || tipo === 'opcion_multiple') {
            $('#editar_opciones_group').show();
            $('#editar_campo_texto_group').hide();
            $('#editar_opciones_inputs').append(crearEditarInputOpcion());
            $('#editar_opciones_inputs').append(crearEditarInputOpcion());
        } else if (tipo === 'si_no') {
            $('#editar_opciones_group').hide();
            $('#editar_campo_texto_group').show();
        } else {
            $('#editar_opciones_group').hide();
            $('#editar_campo_texto_group').hide();
        }
    });

    // Añadir opción en edición
    $('#btnEditarAgregarOpcion').on('click', function() {
        $('#editar_opciones_inputs').append(crearEditarInputOpcion());
    });

    // Quitar opción en edición
    $('#editar_opciones_inputs').on('click', '.btnEditarQuitarOpcion', function() {
        $(this).closest('.editar-opcion-item').remove();
    });

    // Función para crear input de opción en edición
    function crearEditarInputOpcion(valor = '') {
        return `<div class="input-group mb-1 editar-opcion-item">
            <input type="text" name="opciones[]" class="form-control editar-opcion-input" value="${valor}" required>
            <button type="button" class="btn btn-outline-danger btn-sm btnEditarQuitarOpcion" tabindex="-1" title="Quitar opción">
                <i class="fa fa-times"></i>
            </button>
        </div>`;
    }

    // Validación para edición de pregunta
    $('#formEditarPregunta').on('submit', function(e) {
        let tipo = $('#editar_tipo_respuesta').val();
        if (tipo === 'opcion_unica' || tipo === 'opcion_multiple') {
            let opciones = [];
            $('.editar-opcion-input').each(function() {
                let val = $(this).val().trim();
                if (val !== '') opciones.push(val);
            });
            if (opciones.length < 2) {
                alert('Debes agregar al menos dos opciones.');
                e.preventDefault();
                return false;
            }
        }
        e.preventDefault();
        let form = $(this);
        $.ajax({
            url: urls.editar_pregunta_ajax,
            type: "POST",
            data: form.serialize(),
            headers: {'X-CSRFToken': urls.csrf_token},
            success: function(response) {
                if (response.ok) {
                    $('#modalEditarPregunta').modal('hide');
                    location.reload();
                } else {
                    alert('No se pudo editar la pregunta.');
                }
            },
            error: function() {
                alert('Error al editar la pregunta.');
            }
        });
    });

    // Limpiar modal de edición al cerrarlo
    $('#modalEditarPregunta').on('hidden.bs.modal', function () {
        $('#formEditarPregunta')[0].reset();
        $('#editar_opciones_group').hide();
        $('#editar_campo_texto_group').hide();
        $('#editar_opciones_inputs').empty();
    });

    // Limpiar modal de nueva pregunta al cerrarlo
    $('#modalPregunta').on('hidden.bs.modal', function () {
        $('#formNuevaPregunta')[0].reset();
        $('#opciones_group').hide();
        $('#campo_texto_group').hide();
        $('#opciones_inputs').empty();
        actualizarVistaPrevia();
    });

    // Manejo de la gráfica de opciones
    var graficaOpciones = null;

    // Colores personalizados para las barras
    let colores = [
        'rgba(54, 162, 235, 0.7)',
        'rgba(255, 99, 132, 0.7)',
        'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)',
        'rgba(153, 102, 255, 0.7)',
        'rgba(255, 159, 64, 0.7)'
    ];
    let coloresBorde = [
        'rgba(54, 162, 235, 1)',
        'rgba(255, 99, 132, 1)',
        'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)',
        'rgba(153, 102, 255, 1)',
        'rgba(255, 159, 64, 1)'
    ];

    $(document).on('click', '.btnDetallesPregunta', function() {
        let preguntaId = $(this).data('pregunta-id');
        $.get(urls.detalles_pregunta, {pregunta_id: preguntaId}, function(data) {
            $('#modalDetallesPreguntaLabel').text(data.texto_pregunta);

            let labels = data.labels;
            let valores = data.values;

            if (graficaOpciones) {
                graficaOpciones.destroy();
            }
            let ctx = document.getElementById('graficaOpciones').getContext('2d');
            let total = valores.reduce((a, b) => a + b, 0);

            graficaOpciones = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Veces seleccionada',
                        data: valores,
                        backgroundColor: colores.slice(0, labels.length),
                        borderColor: coloresBorde.slice(0, labels.length),
                        borderWidth: 2,
                        borderRadius: 8,
                        hoverBackgroundColor: 'rgba(0,0,0,0.2)'
                    }]
                },
                options: {
                    animation: {
                        duration: 1200,
                        easing: 'easeOutBounce'
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1,
                                callback: function(value) {
                                    if (Number.isInteger(value)) {
                                        return value;
                                    }
                                }
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: true,
                            position: 'top',
                            labels: {
                                font: {
                                    size: 14
                                }
                            }
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    let valor = context.parsed.y;
                                    let porcentaje = total > 0 ? ((valor / total) * 100).toFixed(1) : 0;
                                    return ` ${valor} personas (${porcentaje}%)`;
                                }
                            }
                        },
                        datalabels: {
                            anchor: 'end',
                            align: 'top',
                            font: {
                                weight: 'bold',
                                size: 13
                            },
                            color: '#333',
                            formatter: function(value, context) {
                                let porcentaje = total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                                return `${value} (${porcentaje}%)`;
                            }
                        }
                    }
                },
                plugins: [ChartDataLabels]
            });

            // Botón para exportar la gráfica como imagen
            $('#btnExportarGrafica').off('click').on('click', function() {
                let url_base64 = document.getElementById('graficaOpciones').toDataURL('image/png');
                let a = document.createElement('a');
                a.href = url_base64;
                a.download = 'grafica.png';
                a.click();
            });

            $('#modalDetallesPregunta').modal('show');
        });
    });
});