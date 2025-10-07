jQuery(function ($) {
    $(function () {
      const usuarios = $("#usuarios").DataTable({
        paging: true,
        select: false,
        language: {
          Processing: "Procesando...",
          sLengthMenu: "Mostrar _MENU_ registros",
          sZeroRecords: "No se encontraron resultados",
          sEmptyTable: "Ningún dato disponible en esta tabla",
          sInfo:
            "Mostrando registros del _START_ al _END_ de un total de _TOTAL_ registros",
          sInfoEmpty: "Mostrando registros del 0 al 0 de un total de 0 registros",
          sInfoFiltered: "(filtrado de un total de _MAX_ registros)",
          sInfoPostFix: "",
          sSearch: "Buscar:",
          sUrl: "",
          sInfoThousands: ",",
          sLoadingRecords: "Cargando...",
          paginate: {
            next: '<i class="fa fa-angle-double-right" aria-hidden="true"></i>',
            previous:
              '<i class="fa fa-angle-double-left" aria-hidden="true"></i>',
          },
        },
      });

      // Habilitar/Inhabilitar usuario
      $(document).on("click", ".btn-validar, .btn-invalidar", function (e) {
        e.preventDefault();
        const id = $(this).attr("data-id");
        const accion = $(this).hasClass("btn-validar") ? "habilitar" : "inhabilitar";
        const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]").value;
        $.ajax({
          url: "/usuarios/" + accion + "/" + id + "/",
          method: "POST",
          data: {
            csrfmiddlewaretoken: csrftoken
          },
          success: function (response) {
            window.location.reload();
          },
          error: function () {
            alert("No se pudo cambiar el estado del usuario.");
          }
        });
      });

      $("#btn-descargar").on("click", function () {
        const id = $(this).attr("data-id");
        const csrftoken = document.querySelector(
          "[name=csrfmiddlewaretoken]"
        ).value;
        $.ajax({
          url: "/export_pdf/dictamen/" + id,
          method: "POST",
          beforeSend: function (xhr, settings) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
          },
        }).then(function (response) {
          if(response==="correcto"){
            window.location.reload()
          }
        });
      });

      $('#modalBorrarUsuario').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget);
        var userId = button.data('id');
        var form = document.getElementById('formBorrarUsuario');
        var actionUrl = "/usuarios/borrar/" + userId + "/";
        form.action = actionUrl;
      });

    });
});

document.addEventListener("DOMContentLoaded", function() {
  var toastElList = [].slice.call(document.querySelectorAll('.toast'));
  toastElList.forEach(function(toastEl) {
    var toast = new bootstrap.Toast(toastEl);
    toast.show();
  });
});