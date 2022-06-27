function highlight(w) {
    var x = document.getElementById("about");
    var y = document.getElementById("port");
    var z = document.getElementById("contact");
    if (w.id === x.id) {
        x.style.color = "#1266F1";
        y.style.color = "#000";
        z.style.color = "#000";
    } else if (w.id === y.id) {
        y.style.color = "#1266F1";
        x.style.color = "#000";
        z.style.color = "#000";
    } else {
        z.style.color = "#1266F1";
        x.style.color = "#000";
        y.style.color = "#000";
    }
}

function editField(id) {
    document.getElementById(id).readOnly = document.getElementById(id).readOnly !== true;
}

function changeImage(id) {
    var x = document.getElementById(id);
    if (x.style.display === "none") {
        x.style.display = "block";
      } else {
        x.style.display = "none";
      }
}

function showAppointments(y) {
    var x = document.getElementById("medic_appointments"+y);
    if (x.style.display === "none") {
        x.style.display = "block";
      } else {
        x.style.display = "none";
      }
}