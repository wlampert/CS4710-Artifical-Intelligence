import world.Robot;
import world.World;
import java.util.*;
import java.awt.Point;


public class MyRobotClass extends world.Robot {
	Point end;
	int rows;
	int cols;

	private class Node {
		int x;
		int y;
		int g;
		int h;
		int f;
		String ping;
		Node parent;
		Node(int x, int y, int g, int h, int f, Node parent) {
			this.x = x;
			this.y = y;
			this.f = f;
			this.g = g;
			this.h = h;
			this.parent = parent;
			this.ping = null;
		}

		public void setPing(String s) {
			this.ping = s;
		}
	}

	private class Sort implements Comparator<Node> {
		public int compare(Node a, Node b) {
			int x = a.f - b.f;
			if(x == 0) {
				return a.h - b.h;
			}
			else
				return x;
		}
	}

	public void setMap(int rows, int cols) {
		this.rows = rows;
		this.cols = cols; 
	}

	public void setEndPos(Point end) {
		this.end = end;
	}

	public void moveTo(Node n) {
		ArrayList<Node> path = new ArrayList<Node>();
		path.add(n);
		while(path.get(0).parent != null) {
			path.add(0,path.get(0).parent);
		}
		path.remove(0);
		for(Node x:path) {
			super.move(new Point(x.x, x.y));
		}
	}


	@Override
	public void travelToDestination() {
		PriorityQueue<Node> open = new PriorityQueue<Node>(10, new Sort());
		ArrayList<Node> closed = new ArrayList<Node>();
		Node start = new Node(super.getX(), super.getY(), 0,0,0, null);
		start.ping = "S";
		Node finalNode;
		open.add(start);
		System.out.println("Starting at " + start.x + "," + start.y);
		int w1 = 100;
		int w2 = 128;


		while(open.size() > 0) {
			Node q = open.poll();
			String ping;
			if(q.ping == null) {
				ping = super.pingMap(new Point(q.x,q.y));
				q.setPing(ping);
			}
			else {
				ping = q.ping;
			}
			if(!ping.equals("X")) {
				ArrayList<Node> successors = new ArrayList<Node>();
				//Generate Successors
				for(int i = -1; i < 2; i++) {
					for(int j = -1; j < 2; j++) {
						int x = q.x + i;
						int y = q.y + j;
						if(!(i == 0 && j ==0) && x >= 0 && y >= 0 && x < rows && y < cols) {
							int g = q.g + 1;
							int h = Math.max(Math.abs(x - this.end.x), Math.abs(y - this.end.y));
							//int h = (int)Math.pow((int) Math.pow(Math.abs(x - this.end.x),2) + (int) Math.pow(Math.abs(y - this.end.y),2),.5);
							Node newNode = new Node(x, y, g, h, w1*g+w2*h, q);
							successors.add(newNode);
						}
					}
				}

				for(Node n: successors) {
					if(n.x == this.end.x && n.y == this.end.y) {
						moveTo(n);
						break;
					}
					else {
						boolean skip = false;
						
						for(Node m: closed) {
							if(n.x == m.x && n.y == m.y) {
								skip = true;
								break;
							}
						}
						if(!skip) {
							for(Node m: open) {
								if(n.x == m.x && n.y == m.y) {
									if(m.f <= n.f) {
										skip = true;
										break;
									}
									else
										n.ping = m.ping;
								}
							}
						}
						if(!skip)
							open.add(n);
					}
				}
			}
			closed.add(q);
		}
	}

	public static void main(String[] args) {
		try {
			world.World myWorld = new world.World(args[0], false);
			MyRobotClass myRobot = new MyRobotClass();
			myRobot.addToWorld(myWorld);
			myRobot.setMap(myWorld.numRows(), myWorld.numCols());
			myRobot.setEndPos(myWorld.getEndPos());
			System.out.println("Traveling to " + myWorld.getEndPos());
			myRobot.travelToDestination();
		}
		catch(Exception e) {
			e.printStackTrace();
		}
	}
}