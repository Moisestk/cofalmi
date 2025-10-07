  function formatearFecha(fechaISO) {
    if (!fechaISO) return '<span class="text-muted">Sin fecha</span>';
    const meses = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const partes = fechaISO.split("-");
    if (partes.length !== 3) return fechaISO;
    const anio = partes[0];
    const mes = meses[parseInt(partes[1], 10) - 1];
    const dia = partes[2];
    return `${mes} ${dia}, ${anio}`;
}
  
  document.addEventListener('DOMContentLoaded', (event) => {
                        const fechaCampo = document.getElementById('id_fecha_finalizacion');
                        if (fechaCampo) {
                            const today = new Date();
                            const currentYear = today.getFullYear();
                            const minDate = new Date(currentYear, 0, 1);
                            const minDateFormatted = minDate.toISOString().split('T')[0];
                            const maxDate = new Date(currentYear + 3, 11, 31);
                            const maxDateFormatted = maxDate.toISOString().split('T')[0];
                            const month = String(today.getMonth() + 1).padStart(2, '0');
                            const day = String(today.getDate()).padStart(2, '0');
                            const formattedDate = `${currentYear}-${month}-${day}`;
                            if (!fechaCampo.value) {
                                fechaCampo.value = formattedDate;
                            }
                            fechaCampo.setAttribute('min', minDateFormatted);
                            fechaCampo.setAttribute('max', maxDateFormatted);
                        }
                    });

               document.addEventListener('DOMContentLoaded', function() {
        // Obtenemos el campo de entrada por su ID
        const dateInput = document.getElementById('id_fecha_finalizacion');

        if (dateInput) {
            // Obtenemos la fecha actual en formato YYYY-MM-DD
            const today = new Date();
            const year = today.getFullYear();
            const month = String(today.getMonth() + 1).padStart(2, '0');
            const day = String(today.getDate()).padStart(2, '0');
            const minDate = `${year}-${month}-${day}`;

            // Establecemos el atributo 'min' del campo
            dateInput.setAttribute('min', minDate);
        }
    });

    