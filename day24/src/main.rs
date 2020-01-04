use std::env;
use std::fs;
use std::mem;

const GRID_SIZE: usize = 5;

#[derive(Copy,Clone,PartialEq)]
struct Grid {
    data : [[bool; GRID_SIZE]; GRID_SIZE]
}

impl Grid {

    pub fn new() -> Grid
    {
        Grid { data : [[false;GRID_SIZE];GRID_SIZE]}
    }

    pub fn from_file(filename: &str) -> Grid
    {
        let contents = fs::read_to_string(filename).expect("Unable to read file");

        let lines: Vec<&str> = contents.split('\n').collect();

        let mut grid = Grid::new();

        for i in 0..GRID_SIZE {
            for j in 0..GRID_SIZE {
                let inchar = lines[i].as_bytes()[j] as char;
                grid.data[i][j] = if inchar == '#' { true } else { false };
            }
        }
        grid
    }

    pub fn print(&self)
    {
        for i in 0..GRID_SIZE {
            for j in 0..GRID_SIZE {
                let d = self.data[i][j];

                 if d {print!("#");} else {print!(".");}
            }
            println!();
        }
    }

    pub fn get_biodiversity(&self) -> i32
    {
        let mut biodiversity : i32 = 0;
        let mut factor: i32 = 1;
        for i in 0..GRID_SIZE {
            for j in 0..GRID_SIZE {
                if self.data[i][j] {
                    biodiversity += factor;
                }
                factor *= 2;
            }
        }
        biodiversity
    }
}

fn do_iter(grid_new: &mut Grid, grid_old: &Grid) {

    for i in 0..GRID_SIZE {
        for j in 0..GRID_SIZE {

            let mut n_adjacent: i32 = 0;

            // by default,  state remains
            grid_new.data[i][j] = grid_old.data[i][j];

            if i > 0 && grid_old.data[i-1][j] {
                n_adjacent += 1;
            }
            if i < (GRID_SIZE-1) && grid_old.data[i+1][j] {
                n_adjacent += 1;
            }
            if j > 0 && grid_old.data[i][j-1] {
                n_adjacent += 1;
            }
            if j < (GRID_SIZE-1) && grid_old.data[i][j+1] {
                n_adjacent += 1;
            }

            if grid_old.data[i][j] && n_adjacent != 1 {
                grid_new.data[i][j] = false;
            }

            if !grid_old.data[i][j] && n_adjacent>0 && n_adjacent<3 {
                grid_new.data[i][j] = true;
            }
        }
    }
}

#[derive(Copy,Clone,PartialEq)]
struct LvlGrid {
    data : [[Option<bool>; GRID_SIZE]; GRID_SIZE]
}

impl LvlGrid {

    pub fn new() -> LvlGrid
    {
        let mut newgrid = LvlGrid { data : [[Some(false);GRID_SIZE];GRID_SIZE] };
        newgrid.data[2][2] = None;
        newgrid
    }

    pub fn from_file(filename: &str) -> LvlGrid
    {
        let grid = Grid::from_file(filename);
        let mut lvlgrid = LvlGrid::new();

        for i in 0..GRID_SIZE {
            for j in 0..GRID_SIZE {
                if !(i == 2 && j == 2) {
                    lvlgrid.data[i][j] = Some(grid.data[i][j]);
                }
            }
        }
        lvlgrid
    }

    pub fn print(&self)
    {
        for i in 0..GRID_SIZE {
            for j in 0..GRID_SIZE {
                let c = match self.data[i][j] {
                    Some(d) => if d { '#' } else { '.' },
                    None => '?'
                };
                print!("{}",c);
            }
            println!();
        }
    }

    pub fn row_to_str(&self, i: usize) -> String
    {
        let mut s = "".to_string();
        for j in 0..GRID_SIZE {
            let c = match self.data[i][j] {
                Some(d) => if d { '#' } else { '.' },
                None => '?'
            };
            s.push(c);
        }
        s
    }

    pub fn count_bugs(&self) -> i32
    {
        let mut count : i32 = 0;
        for i in 0..GRID_SIZE {
            for j in 0..GRID_SIZE {
                match self.data[i][j] {
                    Some(d) => if d { count+= 1 },
                    None => {}
                }
            }
        }
        count
    }

    pub fn get(&self, i: usize, j: usize) -> Result<bool,String>
    {
        match self.data[i][j] {
            Some(d) => Ok(d),
            None => Err("No cell at i=2, j=2".to_string())
        }
    }

    pub fn set(&mut self, i: usize, j: usize, val: bool) -> Result<(),String>
    {
        match self.data[i][j] {
            Some(_) => { self.data[i][j] = Some(val);
                         Ok(())
            }
            None => Err("No cell at i=2, j=2".to_string())
        }
    }
}


const N_LEVELS: usize = 203;
const LEVEL0_OFFSET: usize = N_LEVELS/2;

#[derive(Copy,Clone)]
struct RecGrid {
    levels : [LvlGrid; N_LEVELS]
}

impl RecGrid {

    pub fn new() -> RecGrid
    {
        RecGrid { levels : [LvlGrid::new(); N_LEVELS]}
    }

    pub fn from_file(filename: &str) -> RecGrid
    {
        let mut recgrid = RecGrid::new();
        recgrid.levels[LEVEL0_OFFSET] = LvlGrid::from_file(filename);
        recgrid
    }

    fn get_nonzero_levels(&self) -> (usize, usize)
    {
        let mut minlvl = N_LEVELS;
        let mut maxlvl = 0;
        for lvl in 0..N_LEVELS {
            if self.levels[lvl].count_bugs() > 0 {
                if lvl < minlvl {
                    minlvl = lvl;
                }
                if  lvl > maxlvl {
                    maxlvl = lvl;
                }
            }
        }
        (minlvl,maxlvl)
    }

    pub fn print(&self)
    {
        let (minlvl,maxlvl) = self.get_nonzero_levels();
        for lvl in minlvl..(maxlvl+1) {
            println!("Depth {}",(lvl as i32)-(LEVEL0_OFFSET as i32));
            self.levels[lvl].print();
            println!();
        }
    }

    pub fn print_horiz(&self)
    {
        let (minlvl, maxlvl) = self.get_nonzero_levels();
        for lvl in minlvl..(maxlvl+1) {
            print!("Depth {:<2}  ", (lvl as i32)-(LEVEL0_OFFSET as i32));
        }
        println!();

        for i in 0..GRID_SIZE {
            for lvl in minlvl..(maxlvl+1) {
                print!("{:8}  ",self.levels[lvl].row_to_str(i));
            }
            println!();
        }
    }

    pub fn get_nbugs(&self) -> i32
    {
        let mut tot = 0;
        for lvl in self.levels.iter() {
            tot += lvl.count_bugs();
        }
        tot
    }
}


fn do_rec_iter(grid_new: &mut RecGrid, grid_old: &RecGrid) -> Result<(),String> {

    for lvl in 0..N_LEVELS {
        for i in 0..GRID_SIZE {
            for j in 0..GRID_SIZE {
                if i==2 && j==2 {
                    continue;
                }

                let mut n_adjacent : i32 = 0;

                //---------------------------------------------------
                // check left neighbor
                //---------------------------------------------------
                if j==0 {
                    // need to check level outside
                    if  lvl>0 && grid_old.levels[lvl-1].get(2,1)? {
                        n_adjacent += 1;
                    }
                }
                else if i==2 && j==3 {
                    // need to check level inside
                    if lvl<(N_LEVELS-1) {
                        for ii in 0..GRID_SIZE {
                            if grid_old.levels[lvl+1].get(ii,4)? {
                                n_adjacent += 1;
                            }
                        }
                    }
                }
                else {
                    // only need to check this level
                    if grid_old.levels[lvl].get(i,j-1)? {
                        n_adjacent += 1;
                    }
                }

                //---------------------------------------------------
                // check right neighbor
                //---------------------------------------------------
                if j==(GRID_SIZE-1) {
                    // need to check level outside
                    if lvl>0 && grid_old.levels[lvl-1].get(2,3)? {
                        n_adjacent += 1;
                    }
                }
                else if i==2 && j==1 {
                    // need to check level inside
                    if lvl<(N_LEVELS-1) {
                        for ii in 0..GRID_SIZE {
                            if grid_old.levels[lvl+1].get(ii,0)? {
                                n_adjacent += 1;
                            }
                        }
                    }
                }
                else {
                    // only need to check this level
                    if grid_old.levels[lvl].get(i,j+1)? {
                        n_adjacent += 1;
                    }
                }

                //---------------------------------------------------
                // check neighbor below
                //---------------------------------------------------
                if i==0 {
                    // need to check level outside
                    if lvl>0 && grid_old.levels[lvl-1].get(1,2)? {
                        n_adjacent += 1;
                    }
                }
                else if i==3 && j==2 {
                    // need to check level inside
                    if lvl<(N_LEVELS-1) {
                        for jj in 0..GRID_SIZE {
                            if grid_old.levels[lvl+1].get(4,jj)? {
                                n_adjacent += 1;
                            }
                        }
                    }
                }
                else {
                    // only need to check this level
                    if grid_old.levels[lvl].get(i-1,j)? {
                        n_adjacent += 1;
                    }
                }

                //---------------------------------------------------
                // check neighbor above
                //---------------------------------------------------
                if i==(GRID_SIZE-1) {
                    // need to check level outside
                    if lvl>0 && grid_old.levels[lvl-1].get(3,2)? {
                        n_adjacent += 1;
                    }
                }
                else if i==1 && j==2 {
                    // need to check level inside
                    if lvl<(N_LEVELS-1) {
                        for jj in 0..GRID_SIZE {
                            if grid_old.levels[lvl+1].get(0,jj)? {
                                n_adjacent += 1;
                            }
                        }
                    }
                }
                else {
                    // only need to check this level
                    if grid_old.levels[lvl].get(i+1,j)? {
                        n_adjacent += 1;
                    }
                }

                // by default,  state remains
                let currval = grid_old.levels[lvl].get(i,j)?;
                grid_new.levels[lvl].set(i,j,currval)?;

                if currval && n_adjacent != 1 {
                    grid_new.levels[lvl].set(i,j,false)?;
                }

                if !currval && n_adjacent>0 && n_adjacent<3 {
                    grid_new.levels[lvl].set(i,j,true)?;
                }
            }
        }
    }

    Ok(())
}


fn do_pt1(input_file_name: &str) -> Result<(),String> {

    let mut grid = Grid::from_file(input_file_name);

    let mut grid_new = Grid::new();

    let mut grid_history : Vec<Grid> = Vec::new();
    grid_history.push(grid);

    println!("=== Initially ===");
    grid.print();

    let mut niter: i32 = 0;
    let mut done = false;

    let mut period: i32 = -1;
    while !done {

        do_iter(&mut grid_new,&grid);
        niter += 1;

        mem::swap(&mut grid, &mut grid_new);

        for (i,g) in grid_history.iter().enumerate() {
            if g == &grid {
                println!("Grid after {} iterations was equal to grid after {} iterations",niter,i);
                done=true;
                period = niter-(i as i32);
                break;
            }
        }

        grid_history.push(grid);

        // println!("=== Iteration {} ===",niter);
        // grid.print();
        // println!(" Biodiversity: {}", grid.get_biodiversity());
    }
    println!("=== Finally (after {} iterations) ===",niter);
    grid.print();
    println!(" Biodiversity: {}", grid.get_biodiversity());

    println!("Period is {}",period);

    // println!("=== States in cycle ==");
    // for i in 0..period {
    //     println!("=== Iteration {} ===",i);
    //     grid_history[(niter-period + i) as usize].print();
    // }

    Ok(())
}

fn do_pt2(input_file_name: &str) -> Result<(),String> {
    let mut grid = RecGrid::from_file(input_file_name);

    let mut grid_new = RecGrid::new();

    println!("=== Initially ===");
    grid.print_horiz();
    println!("Bugs: {}",grid.get_nbugs());
    println!();

    let niter: i32 = 200;

    for it in 0..niter {

        do_rec_iter(&mut grid_new,&grid)?;

        mem::swap(&mut grid, &mut grid_new);

        println!("=== Iteration {} ===",it);
        grid.print_horiz();
        println!("Bugs: {}",grid.get_nbugs());
        println!();
    }

    println!("=== Finally (after {} iterations) ===",niter);
    grid.print_horiz();
    println!("Bugs: {}",grid.get_nbugs());

    Ok(())
}

fn main() {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        panic!("Insufficient arguments!");
    }

    let input_file_name = &args[1];

    // do_pt1(input_file_name).expect("Failed running for part 1");
    do_pt2(input_file_name).expect("Failed running for part 2");
}
