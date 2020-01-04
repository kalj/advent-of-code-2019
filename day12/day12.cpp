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

typedef std::array<int, 3> vec3;

struct state_t {
  vec3 pos;
  vec3 vel;
};

struct state1d_t {
  int pos;
  int vel;
};

void read_state(std::vector<state_t> &state, std::ifstream &is) {
  std::string line;
  while (std::getline(is, line)) {
    int x, y, z;
    sscanf(line.c_str(), "<x=%d, y=%d, z=%d>", &x, &y, &z);
    state.push_back({{x, y, z}, {0, 0, 0}});
  }
}

void print_state(const std::vector<state_t> &state) {
  for (const state_t &s : state) {
    printf("pos: [%8d, %8d, %8d], vel: [%8d, %8d, %8d]\n", s.pos[0], s.pos[1],
           s.pos[2], s.vel[0], s.vel[1], s.vel[2]);
  }
}

void print_energy(const std::vector<state_t> &state) {
  int totsum = 0;
  for (const state_t &s : state) {
    int pot = abs(s.pos[0]) + abs(s.pos[1]) + abs(s.pos[2]);
    int kin = abs(s.vel[0]) + abs(s.vel[1]) + abs(s.vel[2]);
    int tot = pot * kin;
    totsum += tot;
    printf("pot: %8d, kin: %8d, tot: %8d\n", pot, kin, tot);
  }
  printf("Sum of total energy: %d\n", totsum);
}

bool state_equals(const std::vector<state_t> &state1,
                  const std::vector<state_t> &state2) {
  for (int i = 0; i < state1.size(); i++) {
    if (state1[i].pos != state2[i].pos || state1[i].vel != state2[i].vel)
      return false;
  }

  return true;
}

void iteration(std::vector<state_t> &state) {
  const int nmoons = state.size();

  // apply gravity to velocity
  // for(int i=0; i<nmoons; i++) {
  //   for(int j=0; j<nmoons; j++) {
  //     if(i != j) {
  //       state[i].vel[0] += (state[j].pos[0] > state[i].pos[0]) -
  //       (state[j].pos[0] < state[i].pos[0]); state[i].vel[1] +=
  //       (state[j].pos[1] > state[i].pos[1]) - (state[j].pos[1] <
  //       state[i].pos[1]); state[i].vel[2] += (state[j].pos[2] >
  //       state[i].pos[2]) - (state[j].pos[2] < state[i].pos[2]);
  //     }
  //   }
  // }

  for (int i = 0; i < nmoons; i++) {
    for (int j = 0; j < i; j++) {
      int dx = (state[j].pos[0] > state[i].pos[0]) -
               (state[j].pos[0] < state[i].pos[0]);
      int dy = (state[j].pos[1] > state[i].pos[1]) -
               (state[j].pos[1] < state[i].pos[1]);
      int dz = (state[j].pos[2] > state[i].pos[2]) -
               (state[j].pos[2] < state[i].pos[2]);
      state[i].vel[0] += dx;
      state[j].vel[0] -= dx;
      state[i].vel[1] += dy;
      state[j].vel[1] -= dy;
      state[i].vel[2] += dz;
      state[j].vel[2] -= dz;
    }
  }

  // apply velocity to position
  for (int i = 0; i < nmoons; i++) {
    state[i].pos[0] += state[i].vel[0];
    state[i].pos[1] += state[i].vel[1];
    state[i].pos[2] += state[i].vel[2];
  }
}

//===================================================================
//  1d stuff
//===================================================================

void print_state_1d(const std::vector<state1d_t> &state) {
  for (const state1d_t &s : state) {
    printf("pos: [%8d], vel: [%8d]\n", s.pos, s.vel);
  }
}

bool state_equals_1d(const std::vector<state1d_t> &state1,
                     const std::vector<state1d_t> &state2) {
  for (int i = 0; i < state1.size(); i++) {
    if (state1[i].pos != state2[i].pos || state1[i].vel != state2[i].vel)
      return false;
  }

  return true;
}

void iteration_1d(std::vector<state1d_t> &state) {
  const int nmoons = state.size();

  // apply gravity to velocity
  // for(int i=0; i<nmoons; i++) {
  //   for(int j=0; j<nmoons; j++) {
  //     if(i != j) {
  //       state[i].vel[0] += (state[j].pos[0] > state[i].pos[0]) -
  //       (state[j].pos[0] < state[i].pos[0]); state[i].vel[1] +=
  //       (state[j].pos[1] > state[i].pos[1]) - (state[j].pos[1] <
  //       state[i].pos[1]); state[i].vel[2] += (state[j].pos[2] >
  //       state[i].pos[2]) - (state[j].pos[2] < state[i].pos[2]);
  //     }
  //   }
  // }

  for (int i = 0; i < nmoons; i++) {
    for (int j = 0; j < i; j++) {
      int dx = (state[j].pos > state[i].pos) - (state[j].pos < state[i].pos);
      state[i].vel += dx;
      state[j].vel -= dx;
    }
  }

  // apply velocity to position
  for (int i = 0; i < nmoons; i++) {
    state[i].pos += state[i].vel;
  }
}

void get_factors(std::vector<std::pair<int64_t, int>> &factors, int64_t n) {
  // Print the number of 2s that divide n
  int twos = 0;
  while (n % 2 == 0) {
    twos++;
    n = n / 2;
  }

  if (twos > 0)
    factors.push_back({2, twos});

  // n must be odd at this point. So we can skip
  // one element (Note i = i +2)
  const int imax = int(sqrt(n));
  for (int i = 3; i <= imax; i += 2) {
    // While i divides n, print i and divide n
    while (n % i == 0) {
      auto it = std::find_if(factors.begin(), factors.end(),
                             [=](const auto &p) { return p.first == i; });
      if (it != factors.end()) {
        it->second++;
      } else {
        factors.push_back({i, 1});
      }
      n = n / i;
    }
  }

  // This condition is to handle the case when n
  // is a prime number greater than 2
  if (n > 2) {
    factors.push_back({n,1});
  }
}

int main(int argc, char **argv) {

  if (argc < 2) {
    printf("Too few arguments\n");
    return 1;
  }

  const char *infile = argv[1];

  std::ifstream is(infile);

  std::vector<state_t> state;
  read_state(state, is);

#if 0
  std::vector<state_t> initial_state{state};

  int64_t steps = 0;
  printf("After %ld steps:\n",steps);
  print_state(state);

  while(true) {
    iteration(state);
    steps++;

    if(steps % 100'000'000 == 0) {
      printf("Steps: %ld M\n",steps/1000000);
      print_state(state);
    }

    if(state_equals(state,initial_state)) break;
    // if(steps == 100000000) break;
  }

  printf("After %ld steps:\n",steps);
  print_state(state);
  print_energy(state);
#else

  int64_t periods[3];
  for (int component = 0; component < 3; component++) {

    printf("Finding period of component %d\n", component);

    std::vector<state1d_t> state1d{state.size()};
    for (int i = 0; i < state.size(); i++) {
      state1d[i].pos = state[i].pos[component];
      state1d[i].vel = state[i].vel[component];
    }

    std::vector<state1d_t> initial_state1d{state1d};

    int64_t steps = 0;
    printf("After %ld steps:\n", steps);
    print_state_1d(state1d);

    while (true) {
      iteration_1d(state1d);
      steps++;

      if (steps % 100'000'000 == 0) {
        printf("Steps: %ld M\n", steps / 1000000);
        print_state_1d(state1d);
      }

      if (state_equals_1d(state1d, initial_state1d))
        break;
      // if(steps == 100000000) break;
    }

    printf("Component %d reached initial state after %ld steps\n", component, steps);
    // print_state_1d(state1d);
    periods[component] = steps;
  }

  std::vector<std::pair<int64_t, int>> factors;

  for (int component = 0; component < 3; component++) {
    // factor number
    std::vector<std::pair<int64_t, int>> component_factors;
    get_factors(component_factors, periods[component]);

    std::cout << "Period for component " << component << " = "
              << periods[component] << " = ";
    for (int i = 0; i < component_factors.size(); i++) {
      std::cout << component_factors[i].first;
      if (component_factors[i].second != 1) {
        std::cout << "^(" << component_factors[i].second << ")";
      }

      if(i < component_factors.size()-1) {
        std::cout << " * ";
      }
    }
    std::cout << std::endl;

    // add factors to list
    for(const auto& f : component_factors) {
      auto it = std::find_if(factors.begin(), factors.end(),
                             [=](const auto &p) { return p.first == f.first; });
      if(it != factors.end()) {
        it->second = std::max(it->second,f.second);
      }
      else {
        factors.push_back({f.first, f.second});
      }
    }
  }

  int64_t prod = 1;
  std::cout << std::endl;
  std::cout << "Smallest common period: ";
  for (int i = 0; i < factors.size(); i++) {
    std::cout << factors[i].first;
    if (factors[i].second != 1) {
      std::cout << "^(" << factors[i].second << ")";
    }

    if(i < factors.size()-1) {
      std::cout << " * ";
    }

    for(int j=0; j<factors[i].second; j++)
      prod *= factors[i].first;
  }

  std::cout <<" = " << prod << std::endl;

#endif

  return 0;
}
