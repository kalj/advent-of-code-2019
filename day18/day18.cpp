#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <thread>
#include <vector>

using coord_t = std::array<int,2>;

void get_surrounding_positions(std::vector<coord_t> &surrounding, coord_t pos, int height, int width)
{
  for(int dim=0; dim<2; dim++) {
    for( int o=-1; o<2; o+=2) {
      coord_t newpos{pos};
      newpos[dim] += o;
      if(newpos[0] >= 0 && newpos[0] < height && newpos[1] >= 0 && newpos[1] < width)
        surrounding.push_back(newpos);
    }
  }
}

using map_path_t = std::tuple<std::vector<char>,int>;

// Compares two paths according to length
bool compare_paths(const map_path_t &p1, const map_path_t &p2)
{
  return std::get<1>(p1) < std::get<1>(p2);
}

class Map
{
public:
  Map(const char* infile) {
    std::ifstream is(infile);

    std::string line;
    int nlines = 0;
    int linelen = -1;
    while (std::getline(is, line)) {
      if(linelen < 0) {
        linelen = line.size();
      }

      int oldsize = data.size();
      data.resize(oldsize+line.size());
      for(int i=0; i<line.size(); i++) {
        data[oldsize+i] = line[i];
      }
      nlines++;
    }

    this->width = linelen;
    this->height = nlines;
  }

  void print() const {
    for(int i=0; i< this->height; i++) {
      for (int j=0; j<this->width; j++) {
        putchar(this->data[i*this->width+j]);
      }
      printf("\n");
    }
  }

  char get(coord_t p) const {
    return this->data[p[0]*this->width +p[1]];
  }

  void set(coord_t p, char c) {
    this->data[p[0]*this->width +p[1]] = c;
  }

  coord_t get_first_location(char c) const {
    for(int i=0; i< this->height; i++) {
      for (int j=0; j<this->width; j++) {
        if(this->data[i*this->width+j]==c)
          return coord_t{i,j};
      }
    }

    return coord_t{-1,-1};
  }

  void get_all_locations(std::vector<coord_t>& locations, char c) const {
    for(int i=0; i< this->height; i++) {
      for (int j=0; j<this->width; j++) {
        if(this->data[i*this->width+j]==c)
          locations.push_back(coord_t{i,j});
      }
    }
  }

  void get_accessible_keys(std::vector<std::tuple<char,coord_t,int>> &accessible, coord_t pos) const {

    Map map_copy{*this};

    std::vector<coord_t> wavefronts;
    wavefronts.push_back(pos);

    int nsteps = 1;

    while(wavefronts.size() > 0) {

      std::vector<coord_t> wavefronts_new;
      for(coord_t wpos : wavefronts) {
        std::vector<coord_t> sur;
        get_surrounding_positions(sur, wpos,this->height,this->width);

        for(coord_t pt : sur) {
          char t = map_copy.get(pt);

          if(t == '#' || (t>= 'A' && t<='Z'))
            continue;

          if(t >='a' and t<='z') {
            // we found a key!
            accessible.push_back({t,pt,nsteps});
          }
          else if(t == '.') {
            map_copy.set(pt,'@');
            wavefronts_new.push_back(pt);
          }
        }
      }

      std::swap(wavefronts,wavefronts_new);
      nsteps += 1;
    }
  }


  map_path_t get_shortest_path(coord_t pos, std::vector<char> history = {}, int lvl=0) const
  {
    // printf("%*sEntering get_shortest_path (lvl %d)", 2*lvl,"", lvl);
    // for(auto c : history)
    //   printf(" %c >",c);
    // printf("\n");

    std::vector<std::tuple<char,coord_t,int>> accessible_keys;
    get_accessible_keys(accessible_keys,pos);

    std::vector<map_path_t> paths;

    for(const auto &ak : accessible_keys) {

      const auto& [key, kpos, kdist] = ak;
      Map map_copy(*this);

      // move position and remove key
      map_copy.set(pos,'.');
      map_copy.set(kpos,'@');
      // remove door/block
      coord_t door_location = map_copy.get_first_location(toupper(key));
      if(door_location[0] != -1 && door_location[1] != -1) {
        map_copy.set(door_location,'.');
      }

      std::vector<char> newhist{history};
      newhist.push_back(key);
      auto [path,dist] = map_copy.get_shortest_path(kpos, newhist, lvl+1);
      path.push_back(key);

      paths.push_back({ path, dist+kdist });
    }

    if(paths.size() == 0) {
    // printf("%*sExiting get_shortest_path  (lvl %d)\n", 2*lvl,"", lvl);
      return {{},0};
    }

    std::sort(paths.begin(),paths.end(),compare_paths);

    // printf("%*sExiting get_shortest_path  (lvl %d)\n", 2*lvl,"", lvl);
    return paths[0];
  }


private:
  std::vector<char> data;
  int width;
  int height;
};


int main(int argc, char **argv) {

  if (argc < 2) {
    printf("Too few arguments\n");
    return 1;
  }

  const char *infile = argv[1];

  Map map(infile);

  map.print();

  coord_t initial_pos = map.get_first_location('@');
  printf("Initial pos: [%d, %d]\n",initial_pos[0],initial_pos[1]);

  auto [keys,dist] = map.get_shortest_path(initial_pos);

  std::cout << std::endl;
  std::cout << "Shortest path:";
  for(auto k : keys) {
    std::cout << "  " << k;
  }
  std::cout << std::endl;
  std::cout << "Distance:     " << dist << std::endl;

  return 0;
}
