	.section	__TEXT,__text,regular,pure_instructions
	.build_version macos, 10, 14	sdk_version 10, 14
	.globl	_main                   ## -- Begin function main
	.p2align	4, 0x90
_main:                                  ## @main
	.cfi_startproc
## %bb.0:
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset %rbp, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register %rbp
	subq	$80, %rsp
	movl	$0, -4(%rbp)
	movq	$5, -16(%rbp)
	movl	$4, -20(%rbp)
	movq	$3, -32(%rbp)
	movl	-20(%rbp), %eax
	cltd
	movl	$4294967280, %ecx       ## imm = 0xFFFFFFF0
	idivl	%ecx
	movl	$31, %ecx
	movl	%eax, -60(%rbp)         ## 4-byte Spill
	movl	%ecx, %eax
	cltd
	movl	-60(%rbp), %ecx         ## 4-byte Reload
	idivl	%ecx
	addl	$4294967196, %edx       ## imm = 0xFFFFFF9C
	movl	$4294967270, %esi       ## imm = 0xFFFFFFE6
	movl	%esi, %eax
	movl	%edx, -64(%rbp)         ## 4-byte Spill
	cltd
	movl	-64(%rbp), %esi         ## 4-byte Reload
	idivl	%esi
	movl	%edx, -36(%rbp)
	movq	-32(%rbp), %rdi
	movq	-16(%rbp), %r8
	movq	-16(%rbp), %r9
	xorq	$29, %r9
	orq	%r9, %r8
	andq	%r8, %rdi
	movq	%rdi, -48(%rbp)
	movslq	-36(%rbp), %rdi
	andq	-48(%rbp), %rdi
	movq	%rdi, -56(%rbp)
	movq	-56(%rbp), %rsi
	leaq	L_.str(%rip), %rdi
	movb	$0, %al
	callq	_printf
	xorl	%ecx, %ecx
	movl	%eax, -68(%rbp)         ## 4-byte Spill
	movl	%ecx, %eax
	addq	$80, %rsp
	popq	%rbp
	retq
	.cfi_endproc
                                        ## -- End function
	.section	__TEXT,__cstring,cstring_literals
L_.str:                                 ## @.str
	.asciz	"Answer: %lld\n"


.subsections_via_symbols
