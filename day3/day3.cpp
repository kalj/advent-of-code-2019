#include <cstdio>
#include <vector>
#include <fstream>
#include <sstream>
#include <iostream>
#include <string>
#include <algorithm>

#include <Eigen/Core>

void read_path(std::vector<std::string> &path, std::ifstream &is)
{
  std::string line;
  std::getline(is,line);

  std::stringstream ss(line);
  std::string token;
  while(std::getline(ss,token,',')) {
    path.push_back(token);
  }
}

void get_segments(std::vector<std::pair<Eigen::Vector2i,Eigen::Vector2i>> &segm,
                  const std::vector<std::string> &path)
{
  Eigen::Vector2i coord(0,0);
  Eigen::Vector2i newcoord;

  for(auto p: path) {
    char dir = p[0];
    int len = atoi(&p[1]);

    if(dir == 'R')
      newcoord = Eigen::Vector2i(coord[0]+len,coord[1]);
    else if(dir == 'L')
      newcoord = Eigen::Vector2i(coord[0]-len,coord[1]);
    else if(dir == 'U')
      newcoord = Eigen::Vector2i(coord[0],coord[1]+len);
    else if(dir == 'D')
      newcoord = Eigen::Vector2i(coord[0],coord[1]-len);
    else
      throw std::runtime_error("Invalid direction");

    segm.push_back(std::make_pair(coord,newcoord));
    coord = newcoord;
  }
}

std::vector<Eigen::Vector2i> trace_segment(const std::pair<Eigen::Vector2i,Eigen::Vector2i> &segm)
{
  std::vector<Eigen::Vector2i> coords;

  Eigen::Vector2i diff = segm.second-segm.first;

  Eigen::Vector2i dir(0,0);
  int idx = diff[0] == 0 ?
    1 : // vertical
    0;  // horizontal

  int length=std::abs(diff[idx]);
  dir[idx] = diff[idx]/length;
  for(int i=0; i<=length; i++) {
    coords.push_back(segm.first+i*dir);
  }

  return coords;
}

void intersect_traces(std::vector<Eigen::Vector2i> &intersections,
                      const std::vector<Eigen::Vector2i> &tr1,
                      const std::vector<Eigen::Vector2i> &tr2)
{
  for(const auto& t1: tr1) {
    for(const auto& t2: tr2) {
      if(t1 != Eigen::Vector2i(0,0) && t1 == t2) {
        intersections.push_back(t1);
      }
    }
  }
}

std::vector<Eigen::Vector2i> intersect(const std::pair<Eigen::Vector2i,Eigen::Vector2i> &s1, const std::pair<Eigen::Vector2i,Eigen::Vector2i> &s2)
{
  std::vector<Eigen::Vector2i> intersections;

  const Eigen::Vector2i s1min = s1.first.array().min(s1.second.array());
  const Eigen::Vector2i s1max = s1.first.array().max(s1.second.array());
  const Eigen::Vector2i s2min = s2.first.array().min(s2.second.array());
  const Eigen::Vector2i s2max = s2.first.array().max(s2.second.array());

  if( (s1min[0] <= s2max[0]) && (s2min[0] <= s1max[0]) &&
      (s1min[1] <= s2max[1]) && (s2min[1] <= s1max[1])) {
    const std::vector<Eigen::Vector2i> tr1 = trace_segment(s1);
    const std::vector<Eigen::Vector2i> tr2 = trace_segment(s2);

    intersect_traces(intersections,tr1,tr2);
  }

  return intersections;
}

void find_intersections(std::vector<Eigen::Vector2i> &intersections,
                        const std::vector<std::pair<Eigen::Vector2i,Eigen::Vector2i>> &segm1,
                        const std::vector<std::pair<Eigen::Vector2i,Eigen::Vector2i>> &segm2)
{

  // int nsegm = segm1.size();
  // int i = 0;
  for(const auto& s1 : segm1) {

    // std::cout << "Intersecting with segment "<< i << " of " << nsegm<< std::endl;
    for(const auto& s2 : segm2) {
      std::vector<Eigen::Vector2i> local_intersections = intersect(s1,s2);
      if(local_intersections.size() > 0) {
        intersections.insert( intersections.end(), local_intersections.begin(), local_intersections.end() );
      }
    }
    // i++;
  }
}

void trace_paths(std::vector<Eigen::Vector2i>& coords,
                 const std::vector<std::string> &path)
{
  coords.push_back(Eigen::Vector2i(0,0));
  std::vector<std::pair<Eigen::Vector2i,Eigen::Vector2i>> segm;
  get_segments(segm,path);
  for(const auto& s : segm) {
    const std::vector<Eigen::Vector2i> tr = trace_segment(s);
    coords.insert( coords.end(), tr.begin()+1, tr.end() );
  }
}

int index_of_element(const Eigen::Vector2i& needle,const std::vector<Eigen::Vector2i>& haystack)
{
  const auto it = std::find(haystack.begin(),haystack.end(),needle);
  return std::distance(haystack.begin(),it);
}

int main(int argc, char **argv)
{
  if(argc != 2) return 1;

  const char *infile = argv[1];

  std::ifstream is(infile);

  std::vector<std::string> path1;
  read_path(path1,is);
  std::vector<std::string> path2;
  read_path(path2,is);

  std::vector<Eigen::Vector2i> intersections;
#if 1
  std::vector<std::pair<Eigen::Vector2i,Eigen::Vector2i>> segm1;
  get_segments(segm1,path1);

  std::vector<std::pair<Eigen::Vector2i,Eigen::Vector2i>> segm2;
  get_segments(segm2,path2);

  find_intersections(intersections, segm1, segm2);
#else
  std::vector<Eigen::Vector2i> coords1;
  trace_paths(coords1,path1);

  std::vector<Eigen::Vector2i> coords2;
  trace_paths(coords2,path2);

  intersect_traces(intersections,coords1,coords2);
#endif


#if 0
  std::sort(intersections.begin(), intersections.end(),
            [](const Eigen::Vector2i &i1,const Eigen::Vector2i &i2)->bool{ return i1.lpNorm<1>() < i2.lpNorm<1>(); });

  auto the_is = intersections[0];
  std::cout << "(" <<the_is[0] <<", " << the_is[1] << ") -> " << the_is.lpNorm<1>() << std::endl;
#else
  std::vector<Eigen::Vector2i> coords1;
  trace_paths(coords1,path1);
  std::vector<Eigen::Vector2i> coords2;
  trace_paths(coords2,path2);

  std::sort(intersections.begin(), intersections.end(),
            [&](const Eigen::Vector2i &i1,const Eigen::Vector2i &i2)->bool
            {
              const int steps1 = index_of_element(i1, coords1)+index_of_element(i1, coords2);
              const int steps2 = index_of_element(i2, coords1)+index_of_element(i2, coords2);
              return steps1 < steps2;
            });

  auto the_is = intersections[0];
  std::cout << "(" <<the_is[0] <<", " << the_is[1] << ") -> " << (index_of_element(the_is, coords1)+index_of_element(the_is, coords2)) << std::endl;

#endif

  return 0;
}
