#![crate_type = "lib"]
#![crate_name = "foo"]

extern crate libc;

/*
struct my_struct * func_rw() [struct my_struct *]
	struct my_struct * s [struct my_struct *]
*/
#[link(name="cxx")]
extern "C" {
	pub fn func_rw(s: *mut my_struct) -> *mut my_struct;
}


/*
const struct my_struct * func_ro() [const struct my_struct *]
	const struct my_struct * s [const struct my_struct *]
*/
#[link(name="cxx")]
extern "C" {
	pub fn func_ro(s: *const my_struct) -> *const my_struct;
}


/*
struct my_struct
		int a
		char * rw
		const char * ro
*/
#[repr(C)]
pub struct my_struct {
	a: libc::c_int,
	rw: *mut libc::c_char,
	ro: *const libc::c_char,
}

