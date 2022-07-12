
fn main() {
    println!("Hello, world!");
    let a: i8 = 10;
    // println!(size_of_val(a))
    println!("size of val: {:?}", std::mem::size_of_val(&a));
}
