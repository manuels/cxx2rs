
extern crate libc;

/*
int apply()
	int (*)(int) func [int (*)(int)]
	int x
*/
extern "C" {
	fn apply(func: extern fn(libc::c_int), x: libc::c_int) -> libc::c_int;
}


