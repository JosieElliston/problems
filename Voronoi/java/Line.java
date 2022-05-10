public class Line {
    // Lines are internaly defined by their x and y intercepts
    private double yIntc, xIntc;
    final double INF = Double.POSITIVE_INFINITY;

    // From raw intercepts
    public Line(double yIntc, double xIntc) {
        this.yIntc = yIntc;
		this.xIntc = xIntc;
    }

    // From point on the line and its slope
    public Line(Point p, double slope) {
        if (slope == INF) {
			this.yInt = INF;
			this.xInt = p.x()
		} else if (slope == 0) {
			this.yInt = p.y();
			this.xInt = INF;
		} else {
            this.yInt = p.
        }
    }
    
    // From two points on the line
    public Line(Point p1, Point p2) {
        
    }
}