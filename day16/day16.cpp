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
#include <cstring>

void print_signal(const std::vector<int8_t> &u)
{
    for(auto i : u) {
      std::cout << (int)i;
    }
    std::cout << std::endl;
}

void do_fft_phase_opt(std::vector<int8_t> &u_new, const std::vector<int8_t> &u)
{
  const int n = u.size();
  int a = 0;
  for(int i=n-1; i>=0; i--) {
    a += u[i];
    u_new[i] = int8_t(abs(a) % 10);
  }
}

void do_fft_phase(std::vector<int8_t> &u_new, const std::vector<int8_t> &u, int offset = 0)
{
  const int n = u.size();
  if(offset >= n) {
    do_fft_phase_opt(u_new,u);
  }
  else {
    const std::array<int,4> base_pattern{0,1,0,-1};

    for(int i=0; i<n; i++) {
      int a = 0;
      for(int j=0; j<n; j++) {
        const int coeff = base_pattern[((offset+j+1)/(offset+i+1))%4];
        if(j<i and coeff != 0) std::cout << "Coefficient [" << i << ", " << j << "] = " << coeff << std::endl;
        if(j>=i and coeff != 1) std::cout << "Coefficient [" << i << ", " << j << "] = " << coeff << std::endl;
        a += coeff*u[j];
      }
      u_new[i] = int8_t(abs(a) % 10);
    }
  }
}

void do_part1(const std::vector<int8_t>& input)
{
  std::vector<int8_t> u(input);

  std::cout << "Input:" << std::endl;
  print_signal(u);

  std::vector<int8_t> u_new(u.size());
  int n_phases = 100;

  for(int i=0; i<n_phases; i++) {
    do_fft_phase(u_new, u);
    std::swap(u_new,u);
  }

  std::cout << "After "<< n_phases <<" phase(s):" << std::endl;
  print_signal(u);
}

void do_part2(const std::vector<int8_t>& input)
{
  const int origsize = input.size();

  int offset = 0;
  int factor = 1;
  for(int digit=0; digit<7; digit++) {
    offset += input[6-digit]*factor;
    factor *= 10;
  }
  std::cout << "Offset: " << offset << std::endl;


  const int nreps = 10000;
  const int repeated_size = origsize*nreps;
  const int reduced_size = repeated_size-offset;

  std::cout << "Repeated size: " << repeated_size << std::endl;
  std::cout << "Reduced size: " << reduced_size << std::endl;

  std::vector<int8_t> u(reduced_size);

  // copy first (partial) block
  int input_offset = offset % origsize;
  memcpy(&u[0],&input[input_offset],(origsize-input_offset)*sizeof(int8_t));

  // copy full blocks
  for(int i=0; i<reduced_size;) {
    int input_offset = 0;
    int samples_to_copy = origsize;
    if(i==0) {
      input_offset = offset % origsize;
      samples_to_copy = origsize-input_offset;
    }

    memcpy(&u[i],&input[input_offset],samples_to_copy*sizeof(int8_t));
    i += samples_to_copy;
  }


  std::vector<int8_t> u_new(u.size());
  int n_phases = 100;

  for(int i=0; i<n_phases; i++) {
    std::cout << "phase " << i <<"..."<< std::endl;
    do_fft_phase(u_new, u, offset);
    std::swap(u_new,u);
  }

  std::cout << "Message: ";
  for(int i=0;i<8; i++) {
    std::cout << (int)u[i];
  }
  std::cout << std::endl;

}

int main(int argc, char **argv) {

  if (argc < 2) {
    printf("Too few arguments\n");
    return 1;
  }

  const char *infile = argv[1];

  std::ifstream is(infile);

  std::vector<int8_t> input;

  char c;
  while(is.get(c)) {
    input.push_back(c-48);
  }

  // do_part1(input);
  do_part2(input);

  return 0;
}
