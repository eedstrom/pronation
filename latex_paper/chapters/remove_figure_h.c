#include <stdio.h>

#define LIMIT 1000

int line_loop(void);

int h_check(char line_end[], int len);

int main(void)
{
	while (line_loop() > 0)
		;
}

int line_loop(void)
{
	int c, i, j;

	char line_end[LIMIT];
	for (i = 0; i <= LIMIT; ++i)
		line_end[i] = 0;
	for (i = 0; i <= LIMIT && (c = getchar()) != '\n'; ++i) {
		if (c == EOF)
			return 0;
		line_end[i] = c;
	}
	if (i < 3)
		return 1;
	if (h_check(line_end, i) == 1) {
		line_end[i-3] = '\0';
		printf("%s\n", line_end);
	}
	else
		printf("%s\n", line_end);
	return 1;
}

int h_check(char line_end[], int len)
{
	int i, j, flag;
	char test[3] = {'[', 'h', ']'};

	flag = 0;

	j = 2;

	for (i = len; i >= len-2; --i) {
		if (line_end[i-1] == test[j])
			++flag;
		--j;
	}
	if (flag == 3)
		return 1;
	else
		return 0;
}
