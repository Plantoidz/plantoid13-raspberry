import com.hamoid.*;

VideoExport videoExport;

void setup() {
  size(600, 600);
  videoExport = new VideoExport(this, "hello.mp4");
  videoExport.startMovie();
}
void draw() {
  background(#224488);
  rect(frameCount * frameCount % width, 0, 40, height);
  videoExport.saveFrame();
}
void keyPressed() {
  if (key == 'q') {
    videoExport.endMovie();
    exit();
  }
}
