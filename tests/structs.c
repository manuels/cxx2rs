struct my_struct {
	int a;
	char *rw;
	const char *ro;
};

static char string[] = "foobar";

struct my_struct *
func_rw(struct my_struct *s) {
	s->a = 0xDEADBEEF;
	s->rw = string;

	return s;
}

const struct my_struct *
func_ro(const struct my_struct * s) {
	/* impossible because struct is read-only:
	s->a = 0xDEADBEEF;
	s->rw = string;
	*/

	return s;
}
