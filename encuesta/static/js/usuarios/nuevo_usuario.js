jQuery(function ($) {
  $(function () {
    $("#password1, #password2").on("keyup", function () {
      if ($("#password1").val() != $("#password2").val()) {
        $("#errorConfirm").html("Las contraseñas no coinciden.");
      } else {
        $("#errorConfirm").html("");
      }
    });

    $("#action").on("click", function (e) {
      e.preventDefault();
      if ($("#password1").val() === "") {
        $("#errorPassword").html("Este campo es requerido.");
        return;
      } else {
        $("#errorPassword").html("");
      }
      if ($("#password2").val() === "") {
        $("#errorConfirm").html("Este campo es requerido.");
        return;
      } else {
        $("#errorConfirm").html("");
      }
      if ($("#password1").val() != $("#password2").val()) {
        $("#errorConfirm").html("Las contraseñas no coinciden.");
        return
      } else {
        $("#errorConfirm").html("");
      }
      
        if (verificarPassword($("#password1").val())) {
          $("#changePasswordForm").submit();
        }
    });

    $("#show-pass-p13").on("click", function () {
      $(this).toggleClass("active")
      $("#password").attr("type", function (index, attr) {
        return attr == "text" ? "password" : "text";
      });
    });

    $("#show-pass-p1").on("click", function () {
      $(this).toggleClass("active")
      $("#password1").attr("type", function (index, attr) {
        return attr == "text" ? "password" : "text";
      });
    });

    $("#show-pass-p2").on("click", function () {
      $(this).toggleClass("active")
      $("#password2").attr("type", function (index, attr) {
        return attr == "text" ? "password" : "text";
      });
    });
  });
  function verificarPassword(password) {
    var strength = 0;
    var tips = [];
    var valid = false;

    // Check password length
    if (password.length < 8) {
      tips.push("El password debe tener 8 o más carcateres. ");
    } else {
      strength += 1;
    }

    // Check for mixed case
    if (password.match(/[a-z]/) && password.match(/[A-Z]/)) {
      strength += 1;
    } else {
      tips.push("Debe tener al menos una letra mayúscula y un minúscula");
    }

    // Check for numbers
    if (password.match(/\d/)) {
      strength += 1;
    } else {
      tips.push("Debe incluir al menos un número.");
    }

    // Check for special characters
    if (password.match(/[^a-zA-Z\d]/)) {
      strength += 1;
    } else {
      tips.push("Debe incluir al menos un caracter especial. ");
    }
    if (tips.length > 0) {
      let content = "";
      tips.map((tip) => {
        content += `<li>${tip}</li>`;
      });
      $("#errorPassword").html(content);
    }

    if (strength === 4) {
      valid = true;
    }
    return valid;
  }
});
