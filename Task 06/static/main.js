document.getElementById('autoGps').addEventListener('change', function() {
    document.getElementById('manualLoc').style.display = this.checked ? 'none' : 'block';
});

document.getElementById('mainForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    var f = document.getElementById('inputFile').files[0];
    if (!f) {
        alert('Pick a file');
        return;
    }
    
    document.getElementById('loader').style.display = 'block';
    
    var lat, lon;
    
    if (document.getElementById('autoGps').checked) {
        try {
            var pos = await new Promise(function(ok, fail) {
                navigator.geolocation.getCurrentPosition(ok, fail);
            });
            lat = pos.coords.latitude;
            lon = pos.coords.longitude;
        } catch (err) {
            document.getElementById('loader').style.display = 'none';
            alert('GPS error');
            return;
        }
    } else {
        lat = document.getElementById('latVal').value;
        lon = document.getElementById('lonVal').value;
    }
    
    var fd = new FormData();
    fd.append('file', f);
    fd.append('latitude', lat);
    fd.append('longitude', lon);
    
    try {
        var r = await fetch('/api/detect', { method: 'POST', body: fd });
        document.getElementById('loader').style.display = 'none';
        
        var d = await r.json();
        if (!d.success) {
            alert(d.error);
            return;
        }
        
        if (f.type.indexOf('image') >= 0) {
            document.getElementById('imgBox').style.display = 'block';
            document.getElementById('outImg').src = d.image_path;
        } else {
            document.getElementById('vidBox').style.display = 'block';
            document.getElementById('outVid').src = d.video_path;
        }
        
        if (d.map) {
            document.getElementById('mapBox').innerHTML = d.map;
        }
        
        document.getElementById('outputPanel').style.display = 'block';
    } catch (err) {
        document.getElementById('loader').style.display = 'none';
        alert('Error: ' + err.message);
    }
});
