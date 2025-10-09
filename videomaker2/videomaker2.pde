import ddf.minim.*;
import ddf.minim.analysis.*;
import ddf.minim.effects.*;
import ddf.minim.signals.*;
import ddf.minim.spi.*;
import ddf.minim.ugens.*;

import com.hamoid.*;

VideoExport videoExport;

// Configuration variables
// ------------------------
int canvasWidth = 1080;
int canvasHeight = 1080;

String audioFileName = "/home/patch/plantoidz-pi/drum.wav"; // Audio file in data folder

float fps = 24;
float smoothingFactor = 0.25; // FFT audio analysis smoothing factor
// ------------------------




// Global variables
AudioPlayer track;
FFT fft;
Minim minim;  

// General
int bands = 256; // must be multiple of two
float[] spectrum = new float[bands];
float[] sum = new float[bands];


// Graphics
float unit;
int groundLineY;
PVector center;


void load_img() {
    // load image in the center
    PImage img;
    img = loadImage("/home/patch/plantoidz-pi/pipi.jpeg");
    image(img, 445, 630);
}

void settings() {
  size(canvasWidth, canvasHeight);
  smooth(8);
}



void setup() {

  if(args != null) {
	    println(args);
      audioFileName = args[0];
  } else {
      println("args == null");
  }
  // audioFileName = ....	



  frameRate(fps);

  // Graphics related variable setting
  unit = height / 100; // Everything else can be based around unit to make it change depending on size 
  strokeWeight(unit / 10.24);
  groundLineY = height * 3/4;
  center = new PVector(width / 2, height * 3/4);  

  minim = new Minim(this);
  track = minim.loadFile(audioFileName, 2048);
  
  println("track length == " + track.length());
 
  //track.loop();
  track.play();
 
  fft = new FFT( track.bufferSize(), track.sampleRate() );
 
  fft.linAverages(bands);
 
  // track.cue(60000); // Cue in milliseconds
  
  
  videoExport = new VideoExport(this, "myVideo.mp4");
  videoExport.setFrameRate(5);
  videoExport.startMovie();
  
  

}


int sphereRadius;

float spherePrevX;
float spherePrevY;

int yOffset;

boolean initialStatic = true;
float[] extendingSphereLinesRadius;


void drawStatic() {
 
  if (initialStatic) {
    extendingSphereLinesRadius = new float[241];
 
    for (int angle = 0; angle <= 240; angle += 4) {
      extendingSphereLinesRadius[angle] = map(random(1), 0, 1, sphereRadius, sphereRadius * 7);
    }
 
    initialStatic = false;
  }
  
  
    // More extending lines
  for (int angle = 0; angle <= 240; angle += 4) {

    float x = round(cos(radians(angle + 150)) * sphereRadius + center.x);
    float y = round(sin(radians(angle + 150)) * sphereRadius + groundLineY - yOffset);
 
    float xDestination = x;
    float yDestination = y;
    
    
       // Draw lines in small increments to make it easier to work with 
    for (int i = sphereRadius; i <= extendingSphereLinesRadius[angle]; i++) {
      float x2 = cos(radians(angle + 150)) * i + center.x;
      float y2 = sin(radians(angle + 150)) * i + groundLineY - yOffset;
 
      if (y2 <= getGroundY(x2)) { // Make sure it doesn't go into ground
        xDestination = x2;
        yDestination = y2;
      }
    }
    
    
      stroke(255);
 
    if (y <= getGroundY(x)) {
      line(x, y, xDestination, yDestination);
    }
  }
}



void drawAll(float[] sum) {
  // Center sphere
  sphereRadius = 15 * round(unit);

  spherePrevX = 0;
  spherePrevY = 0;

  yOffset = round(sin(radians(150)) * sphereRadius);

  drawStatic();
 
  // Lines surrounding
  float x = 0;
  float y = 0;
  int surrCount = 1;
  
    boolean direction = false;
 
  while (x < width * 1.5 && x > 0 - width / 2) {

    float surroundingRadius;
 
    float surrRadMin = sphereRadius + sphereRadius * 1/2 * surrCount;
    float surrRadMax = surrRadMin + surrRadMin * 1/8;

    float surrYOffset;
 
    float addon = frameCount * 1.5;
 
    if (direction) {
      addon = addon * 1.5;
    }

    for (float angle = 0; angle <= 240; angle += 1.5) {
 
      surroundingRadius = map(sin(radians(angle * 7 + addon)), -1, 1, surrRadMin, surrRadMax); // Faster rotation through angles, radius oscillates
 
      surrYOffset = sin(radians(150)) * surroundingRadius;

      x = round(cos(radians(angle + 150)) * surroundingRadius + center.x);
      y = round(sin(radians(angle + 150)) * surroundingRadius + getGroundY(x) - surrYOffset);

      noStroke();
      fill(map(surroundingRadius, surrRadMin, surrRadMax, 100, 255));
      circle(x, y, 3 * unit / 10.24);
      noFill();
    }

    direction = !direction;
 
    surrCount += 1;
  }
  
  
    // Lines extending from sphere
  float extendingLinesMin = sphereRadius * 1.3;
  float extendingLinesMax = sphereRadius * 3.5; 
 
  float xDestination;
  float yDestination;
 
  for (int angle = 0; angle <= 240; angle++) {

    float extendingSphereLinesRadius = map(noise(angle * 0.3), 0, 1, extendingLinesMin, extendingLinesMax);
 
    // Radius are mapped differently for highs, mids, and lows - alter higher mapping number for different result (eg. 0.8 to 0.2 in the highs)
    if (sum[0] != 0) {
      if (angle >= 0 && angle <= 30) {
        extendingSphereLinesRadius = map(sum[240 - round(map((angle), 0, 30, 0, 80))], 0, 0.8, extendingSphereLinesRadius - extendingSphereLinesRadius / 8, extendingLinesMax * 1.5); // Highs
      }
 
      else if (angle > 30 && angle <= 90) {
        extendingSphereLinesRadius = map(sum[160 - round(map((angle - 30), 0, 60, 0, 80))], 0, 3, extendingSphereLinesRadius - extendingSphereLinesRadius / 8, extendingLinesMax * 1.5); // Mids
      }
 
      else if (angle > 90 && angle <= 120) {
        extendingSphereLinesRadius = map(sum[80 - round(map((angle - 90), 0, 30, 65, 80))], 0, 40, extendingSphereLinesRadius - extendingSphereLinesRadius / 8, extendingLinesMax * 1.5); // Bass
      }
 
      else if (angle > 120 && angle <= 150) {
        extendingSphereLinesRadius = map(sum[0 + round(map((angle - 120), 0, 30, 0, 15))], 0, 40, extendingSphereLinesRadius - extendingSphereLinesRadius / 8, extendingLinesMax * 1.5); // Bass
      }
 
      else if (angle > 150 && angle <= 210) {
        extendingSphereLinesRadius = map(sum[80 + round(map((angle - 150), 0, 60, 0, 80))], 0, 3, extendingSphereLinesRadius - extendingSphereLinesRadius / 8, extendingLinesMax * 1.5); // Mids
      }
 
      else if (angle > 210) {
        extendingSphereLinesRadius = map(sum[160 + round(map((angle - 210), 0, 30, 0, 80))], 0, 0.8, extendingSphereLinesRadius - extendingSphereLinesRadius / 8, extendingLinesMax * 1.5); // Highs
      }
    }



    x = round(cos(radians(angle + 150)) * sphereRadius + center.x);
    y = round(sin(radians(angle + 150)) * sphereRadius + groundLineY - yOffset);

    xDestination = x;
    yDestination = y;

    for (int i = sphereRadius; i <= extendingSphereLinesRadius; i++) {
      int x2 = round(cos(radians(angle + 150)) * i + center.x);
      int y2 = round(sin(radians(angle + 150)) * i + groundLineY - yOffset);
 
      if (y2 <= getGroundY(x2)) { // Make sure it doesnt go into ground
        xDestination = x2;
        yDestination = y2;
      }
    }
    
        stroke(map(extendingSphereLinesRadius, extendingLinesMin, extendingLinesMax, 200, 255));
 
    if (y <= getGroundY(x))  {
      line(x, y, xDestination, yDestination);
    }
  }

  // Ground line
  for (int groundX = 0; groundX <= width; groundX++) {

    float groundY = getGroundY(groundX);

    noStroke();
    fill(255);
    circle(groundX, groundY, 1.8 * unit / 10.24);
    noFill();
  }
}



// Get the Y position at position X of ground sine wave
float getGroundY(float groundX) {

  float angle = 1.1 * groundX / unit * 10.24;

  float groundY = sin(radians(angle + frameCount * 2)) * unit * 1.25 + groundLineY - unit * 1.25;

  return groundY;
}



void draw() {
  
 
  
  
  fft.forward(track.mix);
 
  spectrum = new float[bands];
 
  for(int i = 0; i < fft.avgSize(); i++)
  {
    spectrum[i] = fft.getAvg(i) / 2;
 
    // Smooth the FFT spectrum data by smoothing factor
    sum[i] += (abs(spectrum[i]) - sum[i]) * smoothingFactor;
  }
 
  // Reset canvas
  fill(0);
  noStroke();
  rect(0, 0, width, height);
  noFill();
 
  drawAll(sum);
  load_img();
  
  videoExport.saveFrame();
  println("track position == " + track.position());
  
  
  
  //close everything is player is at the end of the track
  if (track.position() == track.length()) {
      println("track length == " + track.length());

    videoExport.endMovie();
    exit();
  }
  
  
}
