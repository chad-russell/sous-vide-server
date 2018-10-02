console.log('hi from js!');

var tempInput = document.getElementById('temp_input');
//var server = 'http://192.168.0.7'
var server = 'http://localhost'

function drawPlot() {
  var datas = JSON.parse(this.responseText);

  var temp = {
    x: [],
    y: [],
    name: 'Temperature',
    type: 'scatter',
  };

  var on = {
    x: [],
    y: [],
    mode: 'markers',
    marker: {
      color: 'rgb(234, 153, 153)',
      size: 12
    },
    name: 'Turned on',
    type: 'scatter'
  };

  var off = {
    x: [],
    y: [],
    mode: 'markers',
    marker: {
      color: 'rgb(164, 194, 244)',
      size: 12
    },
    name: 'Turned off',
    type: 'scatter'
  };

  if (datas.length > 0) {
    if (datas[0].on) {
      on.x.push(0);
      on.y.push(0);
    }
    else {
      off.x.push(0);
      off.y.push(0);
    }
  }

  datas.forEach((data, index) => {
    temp.x.push(index);
    temp.y.push(data.temp);

    if (index > 0 && !datas[index - 1].on && datas[index].on) {
      console.log('turned on!')
      on.x.push(index);
      on.y.push(0);
    }
    if (index > 0 && datas[index - 1].on && !datas[index].on) {
      console.log('turned off!')
      off.x.push(index);
      off.y.push(0);
    }
  });

  Plotly.newPlot('plot', [temp, on, off]);
}
var req = new XMLHttpRequest();
req.addEventListener('load', drawPlot);
req.open('GET', server + ':8080/graph_info');
req.send();


function targetTemp() {
  tempInput.value = this.responseText
}
var req = new XMLHttpRequest();
req.addEventListener('load', targetTemp);
req.open('GET', server + ':8080/target');
req.send();

function stop() {
  var req = new XMLHttpRequest();
  req.open('POST', server + ':8080/stop');
  req.send();
}

function startOver() {
  var req = new XMLHttpRequest();
  req.open('POST', server + ':8080/reset');
  req.send();
}

function inc() {
  tempInput.value++;
}

function dec() {
  tempInput.value--;
}

function setTarget() {
  var req = new XMLHttpRequest();
  req.open('POST', server + ':8080/target');
  req.setRequestHeader('Content-type', 'application/json');
  req.send(tempInput.value);
}
