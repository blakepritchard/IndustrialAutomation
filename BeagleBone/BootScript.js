// Setu Values
var strServerIP = '192.168.1.50';
// var strServerIP = '10.165.228.146';


var b = require('bonescript');
var http = require('http');
    

var valueADC1 = '0.0';
var valueADC2 = '0.0';
var valueADC3 = '0.0';
var valueADC4 = '0.0';

var iterationSend = 1;
var iterationRead = 1;

var arrayValuesADC1 = [0, 0, 0, 0, 0, 0]  ; 

var fWeight = 0.0;
var nBase = 0.6;
var nSlope = 23;

var hexLightOn = '\x11';
var hexClear = '\x0C';
var strPad = '                ';

          


var strWelcomeMessage = "Tension Monitor Beta 1.0 Blake P";
var txport = '/dev/ttyO4';
var options = {
    baudrate: 19200
};



// Initialize LEDs
var aPinsLED = {    'light1': { 'red':'P8_13', 'green':'P8_17', 'blue':'P8_19' },
                    'light2': { 'red':'P8_14', 'green':'P8_18'}                     //, 'blue':'P8_5' }
                };
                
var aTimersLED = {};
for(display in aPinsLED )
{
    for(color in aPinsLED[display])
    {
        var strPin = aPinsLED[display][color];
        b.pinMode(strPin, 'out');
        b.digitalWrite(strPin, 0);
        
        aTimersLED[strPin] = null;
    }
}

blinkLED = function(strPin) {
    b.digitalWrite(strPin, 1);
    aTimersLED[strPin] = setTimeout(offLED, 300, strPin);
};


offLED = function(strPin) {
    b.digitalWrite(strPin, 0);
};





  function printAIN1(x) {
      valueADC1 = x.value;
      console.log('x.value = ' + x.value);
      if(x.err){console.log('x.err = ' + x.err);}
      console.log('valueADC inside Read callback='+valueADC1+' at iteration:'+iterationRead);
      
      var diff = (nBase - valueADC1)*nSlope;
      fWeight = diff*diff*diff*diff*diff*diff;
      
  }           


function initSerial()
{
    b.serialOpen(txport, options, onTxSerial);
}
function onTxSerial(x) {
    console.log('tx.event = ' + x.event);
    if(x.err) throw('***FAIL*** ' + JSON.stringify(x));
    if(x.event == 'open') {
        console.log("Opened Serial Port");
        
        // Clear Display
        // var hexClear = '\x0C';
        console.log("Clearing Display");
        b.serialWrite(txport, hexClear, onSerialWrite);
        
        // Turn Light ON
        // var hexLightOn = '\x11';
        console.log("Turning Light ON");
        b.serialWrite(txport, hexLightOn, onSerialWrite);
        
        console.log("Displaying Welcome Message");
         b.serialWrite(txport, strWelcomeMessage, onSerialWrite);
    }
    if(x.event == 'data') {
        console.log('tx (' + x.data.length +
                    ') = ' + x.data.toString('ascii'));
    }
}

function onSerialWrite(x) {
    if(x.err) console.log('onSerialWrite err = ' + x.err);
    // if(x.event == 'callback') setTimeout(writeRepeatedly, 1000);
}  


function updateSerial() {
    if('0.0' == valueADC1)
    {
        console.log('valueADC1 is still unset');
    }
    else
    {
        var lineOne = String("Tension: "+ fWeight.toFixed(4) +strPad).slice(0,16);
        var lineTwo = String("To: "+ strServerIP +strPad).slice(0,16);
        
        // Clear Display
        b.serialWrite(txport, hexClear, onSerialWrite);
        
        // Write to Display
        b.serialWrite(txport, lineOne + lineTwo.slice(0,16), onSerialWrite);
    }
}
 

    

  function updateDashboard()
  {
    // curl -d '{ "auth_token": "YOUR_AUTH_TOKEN", "value": ".75" }' \http://192.168.1.40:3030/widgets/tension
    
    
    
          console.log('SendMsg Iteration : ' + iterationSend);
      iterationSend++;
      
      if('0.0' == valueADC1)
      {
          console.log('valueADC1 is still unset');
      }
      else
      {
          console.log('valueADC before http='+valueADC1);
          console.log("Weight="+fWeight);
          //Get 
          var valuesADC = {ADC1: Number(valueADC1.toFixed(4))};
          var stringValuesADC = JSON.stringify(valuesADC);
          
          
          // Build History Array

          if(arrayValuesADC1.length>9){arrayValuesADC1.pop();}
          arrayValuesADC1.unshift(Number(fWeight.toFixed(4)));
          // arrayValuesADC1[arrayValuesADC1.length] = Number(fWeight.toFixed(4)); //.toPrecision(4);
          
          // var dataGraph = [ { "x": (iterationSend), "y": Number(fWeight.toFixed(4)) } ];
          

         var dataGraph = [
                            { "x": (iterationSend-5), "y": arrayValuesADC1[5] },    // 4096 }  //
                            { "x": (iterationSend-4), "y": arrayValuesADC1[4] },
                            { "x": (iterationSend-3), "y": arrayValuesADC1[3] },
                            { "x": (iterationSend-2), "y": arrayValuesADC1[2] },
                            { "x": (iterationSend-1), "y": arrayValuesADC1[1] },    // 2048},  //
                            { "x": (iterationSend), "y": arrayValuesADC1[0] },      // 1024},  // 

                    ];
     
          var message = {
                auth_token: "YOUR_AUTH_TOKEN",
                current: Number(fWeight.toFixed(4)),
                value: Number(fWeight.toFixed(4)),
                points: dataGraph
              };
          
          var MessageString=JSON.stringify(message);
          
          var headers = {
            'Content-Type': 'application/json',
            'Content-Length': MessageString.length
          };
          
          var options = {
              host: strServerIP,
              port: '3030',
              path: '/widgets/tension',
              method: 'POST',
              headers: headers
              }
          
          
          
          // Setup the request.  The options parameter is
          // the object we defined above.
          var req = http.request(options, function(res) {
            res.setEncoding('utf-8');
          
            var responseString = '';
          
            res.on('data', function(data) {
              responseString += data;
            });
          
            res.on('end', function() {
              console.log(responseString);
              //var resultObject = JSON.parse(responseString);
              //console.log(JSON.stringify(resultObject));
            });
          });
          
          req.on('error', function(e) {
            console.log('problem with request: ' + e.message);
            blinkLED(aPinsLED['light1']['red']);
          });
          
          req.write(MessageString);
          req.end();
          blinkLED(aPinsLED['light1']['green']);
      }
    

  }

  


// POST Raw GPIO Message to BackEnd
  function sendMsg() {
      
      console.log('SendMsg Iteration : ' + iterationSend);
      iterationSend++;
      
      if('0.0' == valueADC1)
      {
          console.log('valueADC1 is still unset');
      }
      else
      {
          console.log('valueADC before http='+valueADC1);
          
          
          var valuesADC = {ADC1: valueADC1};
          var stringValuesADC = JSON.stringify(valuesADC);
          
          var message = {
                process: 'LoadCellTest',
                sender: 'BlakesBeagle', 
                text: stringValuesADC
              };
          
          var MessageString=JSON.stringify(message);
          
          var headers = {
            'Content-Type': 'application/json',
            'Content-Length': MessageString.length
          };
          
          var options = {
              host: strServerIP,
              port: '3000',
              path: '/messages',
              method: 'POST',
              headers: headers
              }
          
          
          
          // Setup the request.  The options parameter is
          // the object we defined above.
          var req = http.request(options, function(res) {
            res.setEncoding('utf-8');
          
            var responseString = '';
          
            res.on('data', function(data) {
              responseString += data;
            });
          
            res.on('end', function() {
              console.log(responseString);
              //var resultObject = JSON.parse(responseString);
              //console.log(JSON.stringify(resultObject));
            });
          });
          
          req.on('error', function(e) {
            console.log('problem with request: ' + e.message);
          });
          
          req.write(MessageString);
          req.end();
          blinkLED(aPinsLED['light2']['green']);          
      }
  
  }
  
function collectGPIO()
{
  console.log("Reading GPIO Iteration: "+iterationRead);
  b.analogRead('P9_33', printAIN1);
  iterationRead++;
}



function displayLocalAddress()
{
    // Get Local IP Address
    var os=require('os');
    var ifaces=os.networkInterfaces();
    var numInterfaces = 0;
    for (var dev in ifaces) 
    {
        var alias=0;
        ifaces[dev].forEach
        (   
            function(details)
            {
                if (details.family=='IPv4') 
                {
                    console.log(dev+(alias?':'+alias:''),details.address);
                    
                    // Send IP Address to Serial Display
                    if('127.0.0.1'!=details.address)
                    {
                        var hexClear = '\x0C';
                        console.log("Clearing Display");
                        b.serialWrite(txport, hexClear, onSerialWrite);
                        
                        updateSerial(details.address);
                    }
                    ++alias;
                    ++numInterfaces;
                }
            }
        );
    }
    if(0==numInterfaces)
    {
        var hexClear = '\x0C';
        console.log("Clearing Display");
        b.serialWrite(txport, hexClear, onSerialWrite);
        updateSerial('No IP Found');
    }

    
}



///////////////////////////////////////////////////////////////////////////////
// Main
var loopRead = setInterval(collectGPIO, 1000);

//  Set Up Serial LCD Interface
initSerial();
setTimeout(displayLocalAddress, 5000);

var loopSerial = setInterval(updateSerial, 1000);

// POST Raw GPIO to BackEnd
var loopSend = setInterval(sendMsg, 2000);

// Update Dashboard
var loopSend = setInterval(updateDashboard, 1000);


function clear(){
    clearInterval(loopRead);
    clearInterval(loopSend);
}

//Uncomment to Shut Down after an Interval
// setTimeout(clear, 600000);   
