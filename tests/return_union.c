// skip
/*
looks like unions are not supported yet in rust:
https://github.com/rust-lang/rust/issues/5492
*/

union my_union {
	int a;
	long b;
};

union my_union
return_union_a() {
	union my_union u = {
		a: 0xDEADBEEF
	};
	return u;
}

union my_union
return_union_b() {
	union my_union u = {
		b: 0xBADEAFFE
	};
	return u;
}
