#include <cstdio>
#include <cstdlib>

// #define LOWER_BOUND 124075
// #define UPPER_BOUND 580769

char digits[7];
bool criterium_pt1(int n) {

  sprintf(digits,"%d",n);

  bool monotonous = true;
  bool repeated = false;
  for(int i=1; i<6; i++) {
    repeated   = repeated   || digits[i] == digits[i-1];
    monotonous = monotonous && digits[i] >= digits[i-1];
  }

  return repeated && monotonous;
}

bool criterium_pt2(int n) {

  sprintf(digits,"%d",n);

  bool monotonous = true;
  bool repeated = false;
  int current_reps = 0;
  for(int i=1; i<6; i++) {
    monotonous = monotonous && digits[i] >= digits[i-1];
    if(digits[i] == digits[i-1]) {
      current_reps++;
    }
    else {
      if(current_reps == 1) {
        repeated = true;
      }
      current_reps = 0;
    }
  }

  // check the last pair
  if(current_reps == 1) {
    repeated = true;
  }

  return monotonous && repeated;
}

int main(int argc, char **argv)
{
  if(argc != 3) {
    fprintf(stderr,"Insufficient arguments\n");
    return 1;
  }

  const int lower_bound = atoi(argv[1]);
  const int upper_bound = atoi(argv[2]);

  int n = 0;
  for(int i=lower_bound; i<=upper_bound; i++) {
    if(criterium_pt2(i)) {
      // printf("%d\n",i);
      n++;
    }
  }

  printf("N: %d\n",n);

  return 0;
}
