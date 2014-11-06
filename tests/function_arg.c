int apply(int (*func)(int), int x) {
	return func(x);
}
