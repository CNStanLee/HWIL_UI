
tests/elfs/mbprofile/hello_lmb.elf:     file format elf32-microblazeel


Disassembly of section .vectors.reset:

00000000 <_start>:
   0:	b0000000 	imm	0
   4:	b8080050 	brai	80	// 50 <_start1>

Disassembly of section .vectors.sw_exception:

00000008 <_vector_sw_exception>:
   8:	b0000000 	imm	0
   c:	b8081904 	brai	6404	// 1904 <_exception_handler>

Disassembly of section .vectors.interrupt:

00000010 <_vector_interrupt>:
  10:	b0000000 	imm	0
  14:	b80804a0 	brai	1184	// 4a0 <__interrupt_handler>

Disassembly of section .vectors.hw_exception:

00000020 <_vector_hw_exception>:
  20:	b0000000 	imm	0
  24:	b808048c 	brai	1164	// 48c <_hw_exception_handler>

Disassembly of section .text:

00000050 <_start1>:
040.000 ns        50:	b0000000 	imm	0
||                54:	31a01b40 	addik	r13, r0, 6976	// 1b40 <completed.4829>
020.000 ns        58:	b0000000 	imm	0
||                5c:	304019f8 	addik	r2, r0, 6648	// 19f8 <force_to_data>
020.000 ns        60:	b0000000 	imm	0
||                64:	302027d8 	addik	r1, r0, 10200
020.000 ns        68:	b0000000 	imm	0
||                6c:	b9f401fc 	brlid	r15, 508	// 268 <_crtinit>
030.000 ns        70:	80000000 	or	r0, r0, r0
||                74:	b0000000 	imm	0
020.000 ns        78:	b9f41680 	brlid	r15, 5760	// 16f8 <exit>
||                7c:	30a30000 	addik	r5, r3, 0

00000080 <_exit>:
002.006 s         80:	b8000000 	bri	0	// 80 <_exit>

00000084 <deregister_tm_clones>:
||                84:	b0000000 	imm	0
020.000 ns        88:	30a01b34 	addik	r5, r0, 6964	// 1b34 <__TMC_END__>
||                8c:	b0000000 	imm	0
020.000 ns        90:	30601b37 	addik	r3, r0, 6967
||                94:	30800006 	addik	r4, r0, 6
020.000 ns        98:	14651800 	rsubk	r3, r5, r3
||                9c:	16432003 	cmpu	r18, r3, r4
010.000 ns        a0:	bcb2002c 	bgei	r18, 44		// cc
||                a4:	b0000000 	imm	0
000.000 ns        a8:	30600000 	addik	r3, r0, 0
||                ac:	bc030020 	beqi	r3, 32		// cc
000.000 ns        b0:	3021ffe4 	addik	r1, r1, -28
||                b4:	f9e10000 	swi	r15, r1, 0
000.000 ns        b8:	99fc1800 	brald	r15, r3
||                bc:	80000000 	or	r0, r0, r0
000.000 ns        c0:	e9e10000 	lwi	r15, r1, 0
||                c4:	b60f0008 	rtsd	r15, 8
030.000 ns        c8:	3021001c 	addik	r1, r1, 28
||                cc:	b60f0008 	rtsd	r15, 8
030.000 ns        d0:	80000000 	or	r0, r0, r0

000000d4 <register_tm_clones>:
||                d4:	b0000000 	imm	0
020.000 ns        d8:	30a01b34 	addik	r5, r0, 6964	// 1b34 <__TMC_END__>
||                dc:	b0000000 	imm	0
020.000 ns        e0:	30601b34 	addik	r3, r0, 6964	// 1b34 <__TMC_END__>
||                e4:	14651800 	rsubk	r3, r5, r3
030.000 ns        e8:	64630202 	bsrai	r3, r3, 2
||                ec:	64c3001f 	bsrli	r6, r3, 31
030.000 ns        f0:	10c61800 	addk	r6, r6, r3
||                f4:	90c60001 	sra	r6, r6
010.000 ns        f8:	bc06002c 	beqi	r6, 44		// 124
||                fc:	b0000000 	imm	0
000.000 ns       100:	30600000 	addik	r3, r0, 0
||               104:	bc030020 	beqi	r3, 32		// 124
000.000 ns       108:	3021ffe4 	addik	r1, r1, -28
||               10c:	f9e10000 	swi	r15, r1, 0
000.000 ns       110:	99fc1800 	brald	r15, r3
||               114:	80000000 	or	r0, r0, r0
000.000 ns       118:	e9e10000 	lwi	r15, r1, 0
||               11c:	b60f0008 	rtsd	r15, 8
030.000 ns       120:	3021001c 	addik	r1, r1, 28
||               124:	b60f0008 	rtsd	r15, 8
030.000 ns       128:	80000000 	or	r0, r0, r0

0000012c <__do_global_dtors_aux>:
||               12c:	b0000000 	imm	0
040.000 ns       130:	e0601b40 	lbui	r3, r0, 6976	// 1b40 <completed.4829>
||               134:	bc2300c4 	bnei	r3, 196		// 1f8
020.000 ns       138:	3021ffdc 	addik	r1, r1, -36
||               13c:	fa61001c 	swi	r19, r1, 28
020.000 ns       140:	b0000000 	imm	0
||               144:	308019d0 	addik	r4, r0, 6608	// 19d0 <__DTOR_END__>
020.000 ns       148:	b0000000 	imm	0
||               14c:	326019cc 	addik	r19, r0, 6604	// 19cc <__DTOR_LIST__>
020.000 ns       150:	b0000000 	imm	0
||               154:	e8601b44 	lwi	r3, r0, 6980	// 1b44 <dtor_idx.4831>
020.000 ns       158:	fac10020 	swi	r22, r1, 32
||               15c:	16732000 	rsubk	r19, r19, r4
020.000 ns       160:	66730202 	bsrai	r19, r19, 2
||               164:	f9e10000 	swi	r15, r1, 0
020.000 ns       168:	3273ffff 	addik	r19, r19, -1
||               16c:	b0000000 	imm	0
020.000 ns       170:	32c019cc 	addik	r22, r0, 6604	// 19cc <__DTOR_LIST__>
||               174:	16531803 	cmpu	r18, r19, r3
020.000 ns       178:	beb20034 	bgeid	r18, 52		// 1ac
||               17c:	30630001 	addik	r3, r3, 1
000.000 ns       180:	64830402 	bslli	r4, r3, 2
||               184:	c884b000 	lw	r4, r4, r22
000.000 ns       188:	b0000000 	imm	0
||               18c:	f8601b44 	swi	r3, r0, 6980	// 1b44 <dtor_idx.4831>
000.000 ns       190:	99fc2000 	brald	r15, r4
||               194:	80000000 	or	r0, r0, r0
000.000 ns       198:	b0000000 	imm	0
||               19c:	e8601b44 	lwi	r3, r0, 6980	// 1b44 <dtor_idx.4831>
000.000 ns       1a0:	16531803 	cmpu	r18, r19, r3
||               1a4:	be52ffdc 	bltid	r18, -36		// 180
020.000 ns       1a8:	30630001 	addik	r3, r3, 1
||               1ac:	b9f4fed8 	brlid	r15, -296	// 84 <deregister_tm_clones>
030.000 ns       1b0:	80000000 	or	r0, r0, r0
||               1b4:	b0000000 	imm	0
020.000 ns       1b8:	30600000 	addik	r3, r0, 0
||               1bc:	be030020 	beqid	r3, 32		// 1dc
010.000 ns       1c0:	e9e10000 	lwi	r15, r1, 0
||               1c4:	b0000000 	imm	0
000.000 ns       1c8:	30a01b34 	addik	r5, r0, 6964	// 1b34 <__TMC_END__>
||               1cc:	b000ffff 	imm	-1
000.000 ns       1d0:	b9f4fe30 	brlid	r15, -464	// 0 <_start>
||               1d4:	80000000 	or	r0, r0, r0
020.000 ns       1d8:	e9e10000 	lwi	r15, r1, 0
||               1dc:	ea61001c 	lwi	r19, r1, 28
020.000 ns       1e0:	eac10020 	lwi	r22, r1, 32
||               1e4:	30600001 	addik	r3, r0, 1
020.000 ns       1e8:	b0000000 	imm	0
||               1ec:	f0601b40 	sbi	r3, r0, 6976	// 1b40 <completed.4829>
020.000 ns       1f0:	b60f0008 	rtsd	r15, 8
||               1f4:	30210024 	addik	r1, r1, 36
000.000 ns       1f8:	b60f0008 	rtsd	r15, 8
||               1fc:	80000000 	or	r0, r0, r0

00000200 <frame_dummy>:
030.000 ns       200:	b0000000 	imm	0
||               204:	30600000 	addik	r3, r0, 0
020.000 ns       208:	3021ffe4 	addik	r1, r1, -28
||               20c:	be030020 	beqid	r3, 32		// 22c
010.000 ns       210:	f9e10000 	swi	r15, r1, 0
||               214:	b0000000 	imm	0
000.000 ns       218:	30c01b48 	addik	r6, r0, 6984	// 1b48 <object.4841>
||               21c:	b0000000 	imm	0
000.000 ns       220:	30a01b34 	addik	r5, r0, 6964	// 1b34 <__TMC_END__>
||               224:	99fc1800 	brald	r15, r3
020.000 ns       228:	80000000 	or	r0, r0, r0
||               22c:	b0000000 	imm	0
020.000 ns       230:	30a01b38 	addik	r5, r0, 6968	// 1b38 <__JCR_END__>
||               234:	e8650000 	lwi	r3, r5, 0
040.000 ns       238:	bc230018 	bnei	r3, 24		// 250
||               23c:	b9f4fe98 	brlid	r15, -360	// d4 <register_tm_clones>
030.000 ns       240:	80000000 	or	r0, r0, r0
||               244:	e9e10000 	lwi	r15, r1, 0
040.000 ns       248:	b60f0008 	rtsd	r15, 8
||               24c:	3021001c 	addik	r1, r1, 28
000.000 ns       250:	b0000000 	imm	0
||               254:	30600000 	addik	r3, r0, 0
000.000 ns       258:	bc03ffe4 	beqi	r3, -28		// 23c
||               25c:	99fc1800 	brald	r15, r3
000.000 ns       260:	80000000 	or	r0, r0, r0
||               264:	b800ffd8 	bri	-40		// 23c

00000268 <_crtinit>:
030.000 ns       268:	2021ffec 	addi	r1, r1, -20
||               26c:	f9e10000 	swi	r15, r1, 0
020.000 ns       270:	b0000000 	imm	0
||               274:	20c01b40 	addi	r6, r0, 6976	// 1b40 <completed.4829>
020.000 ns       278:	b0000000 	imm	0
||               27c:	20e01b40 	addi	r7, r0, 6976	// 1b40 <completed.4829>
020.000 ns       280:	06463800 	rsub	r18, r6, r7
||               284:	bc720014 	blei	r18, 20		// 298
000.000 ns       288:	f8060000 	swi	r0, r6, 0
||               28c:	20c60004 	addi	r6, r6, 4
000.000 ns       290:	06463800 	rsub	r18, r6, r7
||               294:	bc92fff4 	bgti	r18, -12		// 288
040.000 ns       298:	b0000000 	imm	0
||               29c:	20c01b40 	addi	r6, r0, 6976	// 1b40 <completed.4829>
020.000 ns       2a0:	b0000000 	imm	0
||               2a4:	20e01be8 	addi	r7, r0, 7144	// 1be8 <__bss_end>
020.000 ns       2a8:	06463800 	rsub	r18, r6, r7
||               2ac:	bc720014 	blei	r18, 20		// 2c0
001.660 us       2b0:	f8060000 	swi	r0, r6, 0
||               2b4:	20c60004 	addi	r6, r6, 4
840.000 ns       2b8:	06463800 	rsub	r18, r6, r7
||               2bc:	bc92fff4 	bgti	r18, -12		// 2b0
020.000 ns       2c0:	b0000000 	imm	0
||               2c4:	b9f4164c 	brlid	r15, 5708	// 1910 <_program_init>
030.000 ns       2c8:	80000000 	or	r0, r0, r0
||               2cc:	b0000000 	imm	0
020.000 ns       2d0:	b9f41698 	brlid	r15, 5784	// 1968 <__init>
||               2d4:	80000000 	or	r0, r0, r0
030.000 ns       2d8:	20c00000 	addi	r6, r0, 0
||               2dc:	20e00000 	addi	r7, r0, 0
020.000 ns       2e0:	b0000000 	imm	0
||               2e4:	b9f40034 	brlid	r15, 52	// 318 <main>
030.000 ns       2e8:	20a00000 	addi	r5, r0, 0
||               2ec:	32630000 	addik	r19, r3, 0
020.000 ns       2f0:	b0000000 	imm	0
||               2f4:	b9f416b0 	brlid	r15, 5808	// 19a4 <__fini>
030.000 ns       2f8:	80000000 	or	r0, r0, r0
||               2fc:	b0000000 	imm	0
020.000 ns       300:	b9f41608 	brlid	r15, 5640	// 1908 <_program_clean>
||               304:	80000000 	or	r0, r0, r0
030.000 ns       308:	c9e10000 	lw	r15, r1, r0
||               30c:	30730000 	addik	r3, r19, 0
030.000 ns       310:	b60f0008 	rtsd	r15, 8
||               314:	20210014 	addi	r1, r1, 20

00000318 <main>:
030.000 ns       318:	3021ffe0 	addik	r1, r1, -32
||               31c:	f9e10000 	swi	r15, r1, 0
020.000 ns       320:	fa61001c 	swi	r19, r1, 28
||               324:	12610000 	addk	r19, r1, r0
020.000 ns       328:	b0000000 	imm	0
||               32c:	b9f400f0 	brlid	r15, 240	// 41c <init_platform>
030.000 ns       330:	80000000 	or	r0, r0, r0
||               334:	b0000000 	imm	0
020.000 ns       338:	30a019d4 	addik	r5, r0, 6612	// 19d4 <__rodata_start>
||               33c:	b0000000 	imm	0
020.000 ns       340:	b9f40218 	brlid	r15, 536	// 558 <print>
||               344:	80000000 	or	r0, r0, r0
030.000 ns       348:	b0000000 	imm	0
||               34c:	b9f4010c 	brlid	r15, 268	// 458 <cleanup_platform>
030.000 ns       350:	80000000 	or	r0, r0, r0
||               354:	10600000 	addk	r3, r0, r0
020.000 ns       358:	e9e10000 	lwi	r15, r1, 0
||               35c:	10330000 	addk	r1, r19, r0
020.000 ns       360:	ea61001c 	lwi	r19, r1, 28
||               364:	30210020 	addik	r1, r1, 32
020.000 ns       368:	b60f0008 	rtsd	r15, 8
||               36c:	80000000 	or	r0, r0, r0

00000370 <enable_caches>:
030.000 ns       370:	3021fff8 	addik	r1, r1, -8
||               374:	f9e10000 	swi	r15, r1, 0
020.000 ns       378:	fa610004 	swi	r19, r1, 4
||               37c:	12610000 	addk	r19, r1, r0
020.000 ns       380:	b0000000 	imm	0
||               384:	b9f40114 	brlid	r15, 276	// 498 <microblaze_enable_icache>
030.000 ns       388:	80000000 	or	r0, r0, r0
||               38c:	b0000000 	imm	0
020.000 ns       390:	b9f40100 	brlid	r15, 256	// 490 <microblaze_enable_dcache>
||               394:	80000000 	or	r0, r0, r0
030.000 ns       398:	80000000 	or	r0, r0, r0
||               39c:	e9e10000 	lwi	r15, r1, 0
020.000 ns       3a0:	10330000 	addk	r1, r19, r0
||               3a4:	ea610004 	lwi	r19, r1, 4
020.000 ns       3a8:	30210008 	addik	r1, r1, 8
||               3ac:	b60f0008 	rtsd	r15, 8
030.000 ns       3b0:	80000000 	or	r0, r0, r0

000003b4 <disable_caches>:
||               3b4:	3021fff8 	addik	r1, r1, -8
020.000 ns       3b8:	f9e10000 	swi	r15, r1, 0
||               3bc:	fa610004 	swi	r19, r1, 4
020.000 ns       3c0:	12610000 	addk	r19, r1, r0
||               3c4:	b0000000 	imm	0
020.000 ns       3c8:	b9f401d8 	brlid	r15, 472	// 5a0 <Xil_DCacheDisable>
||               3cc:	80000000 	or	r0, r0, r0
030.000 ns       3d0:	b0000000 	imm	0
||               3d4:	b9f4021c 	brlid	r15, 540	// 5f0 <Xil_ICacheDisable>
030.000 ns       3d8:	80000000 	or	r0, r0, r0
||               3dc:	80000000 	or	r0, r0, r0
020.000 ns       3e0:	e9e10000 	lwi	r15, r1, 0
||               3e4:	10330000 	addk	r1, r19, r0
020.000 ns       3e8:	ea610004 	lwi	r19, r1, 4
||               3ec:	30210008 	addik	r1, r1, 8
020.000 ns       3f0:	b60f0008 	rtsd	r15, 8
||               3f4:	80000000 	or	r0, r0, r0

000003f8 <init_uart>:
030.000 ns       3f8:	3021fff8 	addik	r1, r1, -8
||               3fc:	fa610004 	swi	r19, r1, 4
020.000 ns       400:	12610000 	addk	r19, r1, r0
||               404:	80000000 	or	r0, r0, r0
020.000 ns       408:	10330000 	addk	r1, r19, r0
||               40c:	ea610004 	lwi	r19, r1, 4
020.000 ns       410:	30210008 	addik	r1, r1, 8
||               414:	b60f0008 	rtsd	r15, 8
030.000 ns       418:	80000000 	or	r0, r0, r0

0000041c <init_platform>:
||               41c:	3021ffe0 	addik	r1, r1, -32
020.000 ns       420:	f9e10000 	swi	r15, r1, 0
||               424:	fa61001c 	swi	r19, r1, 28
020.000 ns       428:	12610000 	addk	r19, r1, r0
||               42c:	b9f4ff44 	brlid	r15, -188	// 370 <enable_caches>
030.000 ns       430:	80000000 	or	r0, r0, r0
||               434:	b9f4ffc4 	brlid	r15, -60	// 3f8 <init_uart>
030.000 ns       438:	80000000 	or	r0, r0, r0
||               43c:	80000000 	or	r0, r0, r0
020.000 ns       440:	e9e10000 	lwi	r15, r1, 0
||               444:	10330000 	addk	r1, r19, r0
020.000 ns       448:	ea61001c 	lwi	r19, r1, 28
||               44c:	30210020 	addik	r1, r1, 32
020.000 ns       450:	b60f0008 	rtsd	r15, 8
||               454:	80000000 	or	r0, r0, r0

00000458 <cleanup_platform>:
030.000 ns       458:	3021ffe0 	addik	r1, r1, -32
||               45c:	f9e10000 	swi	r15, r1, 0
020.000 ns       460:	fa61001c 	swi	r19, r1, 28
||               464:	12610000 	addk	r19, r1, r0
020.000 ns       468:	b9f4ff4c 	brlid	r15, -180	// 3b4 <disable_caches>
||               46c:	80000000 	or	r0, r0, r0
030.000 ns       470:	80000000 	or	r0, r0, r0
||               474:	e9e10000 	lwi	r15, r1, 0
020.000 ns       478:	10330000 	addk	r1, r19, r0
||               47c:	ea61001c 	lwi	r19, r1, 28
020.000 ns       480:	30210020 	addik	r1, r1, 32
||               484:	b60f0008 	rtsd	r15, 8
010.000 ns       488:	80000000 	or	r0, r0, r0

0000048c <_hw_exception_handler>:
||               48c:	b8000000 	bri	0	// 48c <_hw_exception_handler>

00000490 <microblaze_enable_dcache>:
030.000 ns       490:	b60f0008 	rtsd	r15, 8
||               494:	94100080 	msrset	r0, 128

00000498 <microblaze_enable_icache>:
030.000 ns       498:	b60f0008 	rtsd	r15, 8
||               49c:	94100020 	msrset	r0, 32

000004a0 <__interrupt_handler>:
000.000 ns       4a0:	3021ffac 	addik	r1, r1, -84
||               4a4:	f9e10000 	swi	r15, r1, 0
000.000 ns       4a8:	f8210020 	swi	r1, r1, 32
||               4ac:	f8610024 	swi	r3, r1, 36
000.000 ns       4b0:	f8810028 	swi	r4, r1, 40
||               4b4:	f8a1002c 	swi	r5, r1, 44
000.000 ns       4b8:	f8c10030 	swi	r6, r1, 48
||               4bc:	f8e10034 	swi	r7, r1, 52
000.000 ns       4c0:	f9010038 	swi	r8, r1, 56
||               4c4:	f921003c 	swi	r9, r1, 60
000.000 ns       4c8:	f9410040 	swi	r10, r1, 64
||               4cc:	b0000000 	imm	0
000.000 ns       4d0:	30601a00 	addik	r3, r0, 6656	// 1a00 <MB_InterruptVectorTable>
||               4d4:	f9610044 	swi	r11, r1, 68
000.000 ns       4d8:	f9810048 	swi	r12, r1, 72
||               4dc:	fa21004c 	swi	r17, r1, 76
000.000 ns       4e0:	95608001 	mfs	r11, rmsr
||               4e4:	e8830000 	lwi	r4, r3, 0
000.000 ns       4e8:	e8a30004 	lwi	r5, r3, 4
||               4ec:	fa410050 	swi	r18, r1, 80
000.000 ns       4f0:	f961001c 	swi	r11, r1, 28
||               4f4:	99fc2000 	brald	r15, r4
000.000 ns       4f8:	80000000 	or	r0, r0, r0
||               4fc:	e9e10000 	lwi	r15, r1, 0
000.000 ns       500:	e961001c 	lwi	r11, r1, 28
||               504:	e8210020 	lwi	r1, r1, 32
000.000 ns       508:	940bc001 	mts	rmsr, r11
||               50c:	e8610024 	lwi	r3, r1, 36
000.000 ns       510:	e8810028 	lwi	r4, r1, 40
||               514:	e8a1002c 	lwi	r5, r1, 44
000.000 ns       518:	e8c10030 	lwi	r6, r1, 48
||               51c:	e8e10034 	lwi	r7, r1, 52
000.000 ns       520:	e9010038 	lwi	r8, r1, 56
||               524:	e921003c 	lwi	r9, r1, 60
000.000 ns       528:	e9410040 	lwi	r10, r1, 64
||               52c:	e9610044 	lwi	r11, r1, 68
000.000 ns       530:	e9810048 	lwi	r12, r1, 72
||               534:	ea21004c 	lwi	r17, r1, 76
000.000 ns       538:	ea410050 	lwi	r18, r1, 80
||               53c:	b62e0000 	rtid	r14, 0
000.000 ns       540:	30210054 	addik	r1, r1, 84

00000544 <microblaze_register_handler>:
||               544:	b0000000 	imm	0
000.000 ns       548:	30601a00 	addik	r3, r0, 6656	// 1a00 <MB_InterruptVectorTable>
||               54c:	f8a30000 	swi	r5, r3, 0
000.000 ns       550:	b60f0008 	rtsd	r15, 8
||               554:	f8c30004 	swi	r6, r3, 4

00000558 <print>:
030.000 ns       558:	3021fff8 	addik	r1, r1, -8
||               55c:	fa610004 	swi	r19, r1, 4
020.000 ns       560:	f9e10000 	swi	r15, r1, 0
||               564:	12650000 	addk	r19, r5, r0
040.000 ns       568:	e0a50000 	lbui	r5, r5, 0
||               56c:	90a50060 	sext8	r5, r5
020.000 ns       570:	be050024 	beqid	r5, 36		// 594
||               574:	e9e10000 	lwi	r15, r1, 0
380.000 ns       578:	b0000000 	imm	0
||               57c:	b9f4048c 	brlid	r15, 1164	// a08 <outbyte>
390.000 ns       580:	32730001 	addik	r19, r19, 1
||               584:	e0b30000 	lbui	r5, r19, 0
520.000 ns       588:	90a50060 	sext8	r5, r5
||               58c:	be25ffec 	bneid	r5, -20		// 578
140.000 ns       590:	e9e10000 	lwi	r15, r1, 0
||               594:	ea610004 	lwi	r19, r1, 4
030.000 ns       598:	b60f0008 	rtsd	r15, 8
||               59c:	30210008 	addik	r1, r1, 8

000005a0 <Xil_DCacheDisable>:
030.000 ns       5a0:	3021fffc 	addik	r1, r1, -4
||               5a4:	f9e10000 	swi	r15, r1, 0
020.000 ns       5a8:	b0000000 	imm	0
||               5ac:	b9f403fc 	brlid	r15, 1020	// 9a8 <microblaze_flush_cache_ext>
030.000 ns       5b0:	80000000 	or	r0, r0, r0
||               5b4:	b0000000 	imm	0
020.000 ns       5b8:	b9f40400 	brlid	r15, 1024	// 9b8 <microblaze_invalidate_dcache>
||               5bc:	80000000 	or	r0, r0, r0
030.000 ns       5c0:	b0000000 	imm	0
||               5c4:	b9f403ec 	brlid	r15, 1004	// 9b0 <microblaze_invalidate_cache_ext>
030.000 ns       5c8:	80000000 	or	r0, r0, r0
||               5cc:	b0000000 	imm	0
020.000 ns       5d0:	b9f403e8 	brlid	r15, 1000	// 9b8 <microblaze_invalidate_dcache>
||               5d4:	80000000 	or	r0, r0, r0
030.000 ns       5d8:	b0000000 	imm	0
||               5dc:	b9f403bc 	brlid	r15, 956	// 998 <microblaze_disable_dcache>
030.000 ns       5e0:	80000000 	or	r0, r0, r0
||               5e4:	e9e10000 	lwi	r15, r1, 0
040.000 ns       5e8:	b60f0008 	rtsd	r15, 8
||               5ec:	30210004 	addik	r1, r1, 4

000005f0 <Xil_ICacheDisable>:
030.000 ns       5f0:	3021fffc 	addik	r1, r1, -4
||               5f4:	f9e10000 	swi	r15, r1, 0
020.000 ns       5f8:	b0000000 	imm	0
||               5fc:	b9f403b4 	brlid	r15, 948	// 9b0 <microblaze_invalidate_cache_ext>
030.000 ns       600:	80000000 	or	r0, r0, r0
||               604:	b0000000 	imm	0
020.000 ns       608:	b9f403d8 	brlid	r15, 984	// 9e0 <microblaze_invalidate_icache>
||               60c:	80000000 	or	r0, r0, r0
030.000 ns       610:	b0000000 	imm	0
||               614:	b9f4038c 	brlid	r15, 908	// 9a0 <microblaze_disable_icache>
030.000 ns       618:	80000000 	or	r0, r0, r0
||               61c:	e9e10000 	lwi	r15, r1, 0
040.000 ns       620:	b60f0008 	rtsd	r15, 8
||               624:	30210004 	addik	r1, r1, 4

00000628 <XIntc_DeviceInterruptHandler>:
000.000 ns       628:	60650030 	muli	r3, r5, 48
||               62c:	3021ffc4 	addik	r1, r1, -60
000.000 ns       630:	f9e10000 	swi	r15, r1, 0
||               634:	fa61001c 	swi	r19, r1, 28
000.000 ns       638:	fac10020 	swi	r22, r1, 32
||               63c:	fae10024 	swi	r23, r1, 36
000.000 ns       640:	fb010028 	swi	r24, r1, 40
||               644:	fb21002c 	swi	r25, r1, 44
000.000 ns       648:	fb410030 	swi	r26, r1, 48
||               64c:	fb610034 	swi	r27, r1, 52
000.000 ns       650:	fb810038 	swi	r28, r1, 56
||               654:	b0000000 	imm	0
000.000 ns       658:	30631a08 	addik	r3, r3, 6664
||               65c:	e8830004 	lwi	r4, r3, 4
000.000 ns       660:	e863000c 	lwi	r3, r3, 12
||               664:	e8c40000 	lwi	r6, r4, 0
000.000 ns       668:	ea640008 	lwi	r19, r4, 8
||               66c:	a8630001 	xori	r3, r3, 1
000.000 ns       670:	be0300fc 	beqid	r3, 252		// 76c
||               674:	86733000 	and	r19, r19, r6
000.000 ns       678:	63050030 	muli	r24, r5, 48
||               67c:	12c00000 	addk	r22, r0, r0
000.000 ns       680:	b0000000 	imm	0
||               684:	33181a08 	addik	r24, r24, 6664
000.000 ns       688:	e8780014 	lwi	r3, r24, 20
||               68c:	be6300b4 	bleid	r3, 180		// 740
000.000 ns       690:	32e00001 	addik	r23, r0, 1
||               694:	33580008 	addik	r26, r24, 8
000.000 ns       698:	33780004 	addik	r27, r24, 4
||               69c:	33980018 	addik	r28, r24, 24
000.000 ns       6a0:	63250006 	muli	r25, r5, 6
||               6a4:	b8100018 	brid	24		// 6bc
000.000 ns       6a8:	33180014 	addik	r24, r24, 20
||               6ac:	e8780000 	lwi	r3, r24, 0
000.000 ns       6b0:	1643b001 	cmp	r18, r3, r22
||               6b4:	beb20090 	bgeid	r18, 144		// 744
000.000 ns       6b8:	e9e10000 	lwi	r15, r1, 0
||               6bc:	1079b000 	addk	r3, r25, r22
000.000 ns       6c0:	64830403 	bslli	r4, r3, 3
||               6c4:	10640000 	addk	r3, r4, r0
000.000 ns       6c8:	a4b30001 	andi	r5, r19, 1
||               6cc:	b0000000 	imm	0
000.000 ns       6d0:	30841a28 	addik	r4, r4, 6696
||               6d4:	b0000000 	imm	0
000.000 ns       6d8:	30631a08 	addik	r3, r3, 6664
||               6dc:	92730041 	srl	r19, r19
000.000 ns       6e0:	be050058 	beqid	r5, 88		// 738
||               6e4:	32d60001 	addik	r22, r22, 1
000.000 ns       6e8:	e8ba0000 	lwi	r5, r26, 0
||               6ec:	84b72800 	and	r5, r23, r5
000.000 ns       6f0:	bc05000c 	beqi	r5, 12		// 6fc
||               6f4:	e8bb0000 	lwi	r5, r27, 0
000.000 ns       6f8:	fae5000c 	swi	r23, r5, 12
||               6fc:	e8840000 	lwi	r4, r4, 0
000.000 ns       700:	99fc2000 	brald	r15, r4
||               704:	e8a30024 	lwi	r5, r3, 36
000.000 ns       708:	e87a0000 	lwi	r3, r26, 0
||               70c:	84771800 	and	r3, r23, r3
000.000 ns       710:	bc23000c 	bnei	r3, 12		// 71c
||               714:	e87b0000 	lwi	r3, r27, 0
000.000 ns       718:	fae3000c 	swi	r23, r3, 12
||               71c:	e89b0000 	lwi	r4, r27, 0
000.000 ns       720:	e87c0000 	lwi	r3, r28, 0
||               724:	e8a40000 	lwi	r5, r4, 0
000.000 ns       728:	e8840008 	lwi	r4, r4, 8
||               72c:	a8630001 	xori	r3, r3, 1
000.000 ns       730:	be030014 	beqid	r3, 20		// 744
||               734:	e9e10000 	lwi	r15, r1, 0
000.000 ns       738:	be33ff74 	bneid	r19, -140		// 6ac
||               73c:	12f7b800 	addk	r23, r23, r23
000.000 ns       740:	e9e10000 	lwi	r15, r1, 0
||               744:	ea61001c 	lwi	r19, r1, 28
000.000 ns       748:	eac10020 	lwi	r22, r1, 32
||               74c:	eae10024 	lwi	r23, r1, 36
000.000 ns       750:	eb010028 	lwi	r24, r1, 40
||               754:	eb21002c 	lwi	r25, r1, 44
000.000 ns       758:	eb410030 	lwi	r26, r1, 48
||               75c:	eb610034 	lwi	r27, r1, 52
000.000 ns       760:	eb810038 	lwi	r28, r1, 56
||               764:	b60f0008 	rtsd	r15, 8
000.000 ns       768:	3021003c 	addik	r1, r1, 60
||               76c:	e8640020 	lwi	r3, r4, 32
000.000 ns       770:	a863ffff 	xori	r3, r3, -1
||               774:	b810ff04 	brid	-252		// 678
000.000 ns       778:	86731800 	and	r19, r19, r3

0000077c <XIntc_LowLevelInterruptHandler>:
||               77c:	3021ffe4 	addik	r1, r1, -28
000.000 ns       780:	f9e10000 	swi	r15, r1, 0
||               784:	b9f4fea4 	brlid	r15, -348	// 628 <XIntc_DeviceInterruptHandler>
000.000 ns       788:	10a00000 	addk	r5, r0, r0
||               78c:	e9e10000 	lwi	r15, r1, 0
000.000 ns       790:	b60f0008 	rtsd	r15, 8
||               794:	3021001c 	addik	r1, r1, 28

00000798 <XIntc_SetIntrSvcOption>:
000.000 ns       798:	b0000000 	imm	0
||               79c:	e8601a0c 	lwi	r3, r0, 6668
000.000 ns       7a0:	88a51800 	xor	r5, r5, r3
||               7a4:	bc05000c 	beqi	r5, 12		// 7b0
000.000 ns       7a8:	b60f0008 	rtsd	r15, 8
||               7ac:	80000000 	or	r0, r0, r0
000.000 ns       7b0:	b0000000 	imm	0
||               7b4:	f8c01a20 	swi	r6, r0, 6688
000.000 ns       7b8:	b60f0008 	rtsd	r15, 8
||               7bc:	80000000 	or	r0, r0, r0

000007c0 <XIntc_RegisterHandler>:
000.000 ns       7c0:	b0000000 	imm	0
||               7c4:	e8601a0c 	lwi	r3, r0, 6668
000.000 ns       7c8:	88a51800 	xor	r5, r5, r3
||               7cc:	bc05000c 	beqi	r5, 12		// 7d8
000.000 ns       7d0:	b60f0008 	rtsd	r15, 8
||               7d4:	80000000 	or	r0, r0, r0
000.000 ns       7d8:	3060001f 	addik	r3, r0, 31
||               7dc:	16461801 	cmp	r18, r6, r3
000.000 ns       7e0:	be520020 	bltid	r18, 32	// 800 <_HEAP_SIZE>
||               7e4:	64660403 	bslli	r3, r6, 3
000.000 ns       7e8:	b0000000 	imm	0
||               7ec:	f8e31a28 	swi	r7, r3, 6696
000.000 ns       7f0:	b0000000 	imm	0
||               7f4:	f9031a2c 	swi	r8, r3, 6700
000.000 ns       7f8:	b60f0008 	rtsd	r15, 8
||               7fc:	80000000 	or	r0, r0, r0
000.000 ns       800:	3021fff0 	addik	r1, r1, -16
||               804:	64a60205 	bsrai	r5, r6, 5
000.000 ns       808:	fa610004 	swi	r19, r1, 4
||               80c:	12660000 	addk	r19, r6, r0
000.000 ns       810:	b0000000 	imm	0
||               814:	a4a5ffff 	andi	r5, r5, -1
000.000 ns       818:	f9e10000 	swi	r15, r1, 0
||               81c:	fac10008 	swi	r22, r1, 8
000.000 ns       820:	fae1000c 	swi	r23, r1, 12
||               824:	12c70000 	addk	r22, r7, r0
000.000 ns       828:	b0000000 	imm	0
||               82c:	b9f40ad4 	brlid	r15, 2772	// 1300 <XIntc_LookupConfig>
000.000 ns       830:	12e80000 	addk	r23, r8, r0
||               834:	a4d3001f 	andi	r6, r19, 31
000.000 ns       838:	30860004 	addik	r4, r6, 4
||               83c:	64840403 	bslli	r4, r4, 3
000.000 ns       840:	64c60403 	bslli	r6, r6, 3
||               844:	dac41800 	sw	r22, r4, r3
000.000 ns       848:	10633000 	addk	r3, r3, r6
||               84c:	fae30024 	swi	r23, r3, 36
000.000 ns       850:	e9e10000 	lwi	r15, r1, 0
||               854:	ea610004 	lwi	r19, r1, 4
000.000 ns       858:	eac10008 	lwi	r22, r1, 8
||               85c:	eae1000c 	lwi	r23, r1, 12
000.000 ns       860:	b60f0008 	rtsd	r15, 8
||               864:	30210010 	addik	r1, r1, 16

00000868 <XIntc_RegisterFastHandler>:
000.000 ns       868:	3060001f 	addik	r3, r0, 31
||               86c:	16461803 	cmpu	r18, r6, r3
000.000 ns       870:	bc520084 	blti	r18, 132		// 8f4
||               874:	64c60402 	bslli	r6, r6, 2
000.000 ns       878:	b0000000 	imm	0
||               87c:	30661b64 	addik	r3, r6, 7012
000.000 ns       880:	e8850008 	lwi	r4, r5, 8
||               884:	e8630000 	lwi	r3, r3, 0
000.000 ns       888:	84832000 	and	r4, r3, r4
||               88c:	be040048 	beqid	r4, 72		// 8d4
000.000 ns       890:	30850100 	addik	r4, r5, 256
||               894:	e9050008 	lwi	r8, r5, 8
000.000 ns       898:	a883ffff 	xori	r4, r3, -1
||               89c:	31250100 	addik	r9, r5, 256
000.000 ns       8a0:	84844000 	and	r4, r4, r8
||               8a4:	f8850008 	swi	r4, r5, 8
000.000 ns       8a8:	d8e93000 	sw	r7, r9, r6
||               8ac:	e8850020 	lwi	r4, r5, 32
000.000 ns       8b0:	85034000 	and	r8, r3, r8
||               8b4:	80832000 	or	r4, r3, r4
000.000 ns       8b8:	f8850020 	swi	r4, r5, 32
||               8bc:	bc080030 	beqi	r8, 48		// 8ec
000.000 ns       8c0:	e8850008 	lwi	r4, r5, 8
||               8c4:	80632000 	or	r3, r3, r4
000.000 ns       8c8:	f8650008 	swi	r3, r5, 8
||               8cc:	b60f0008 	rtsd	r15, 8
000.000 ns       8d0:	80000000 	or	r0, r0, r0
||               8d4:	d8e62000 	sw	r7, r6, r4
000.000 ns       8d8:	e8850020 	lwi	r4, r5, 32
||               8dc:	80641800 	or	r3, r4, r3
000.000 ns       8e0:	f8650020 	swi	r3, r5, 32
||               8e4:	b60f0008 	rtsd	r15, 8
000.000 ns       8e8:	80000000 	or	r0, r0, r0
||               8ec:	b60f0008 	rtsd	r15, 8
000.000 ns       8f0:	80000000 	or	r0, r0, r0
||               8f4:	3021fff4 	addik	r1, r1, -12
000.000 ns       8f8:	64a60005 	bsrli	r5, r6, 5
||               8fc:	fa610004 	swi	r19, r1, 4
000.000 ns       900:	12660000 	addk	r19, r6, r0
||               904:	fac10008 	swi	r22, r1, 8
000.000 ns       908:	f9e10000 	swi	r15, r1, 0
||               90c:	b0000000 	imm	0
000.000 ns       910:	b9f409f0 	brlid	r15, 2544	// 1300 <XIntc_LookupConfig>
||               914:	12c70000 	addk	r22, r7, r0
000.000 ns       918:	a4d3001f 	andi	r6, r19, 31
||               91c:	e8630004 	lwi	r3, r3, 4
000.000 ns       920:	64c60402 	bslli	r6, r6, 2
||               924:	b0000000 	imm	0
000.000 ns       928:	30a61b64 	addik	r5, r6, 7012
||               92c:	e8830008 	lwi	r4, r3, 8
000.000 ns       930:	e8a50000 	lwi	r5, r5, 0
||               934:	84e52000 	and	r7, r5, r4
000.000 ns       938:	bc270028 	bnei	r7, 40		// 960
||               93c:	30830100 	addik	r4, r3, 256
000.000 ns       940:	dac62000 	sw	r22, r6, r4
||               944:	3080ffff 	addik	r4, r0, -1
000.000 ns       948:	f8830020 	swi	r4, r3, 32
||               94c:	e9e10000 	lwi	r15, r1, 0
000.000 ns       950:	ea610004 	lwi	r19, r1, 4
||               954:	eac10008 	lwi	r22, r1, 8
000.000 ns       958:	b60f0008 	rtsd	r15, 8
||               95c:	3021000c 	addik	r1, r1, 12
000.000 ns       960:	a8e5ffff 	xori	r7, r5, -1
||               964:	84e72000 	and	r7, r7, r4
000.000 ns       968:	f8e30008 	swi	r7, r3, 8
||               96c:	30e30100 	addik	r7, r3, 256
000.000 ns       970:	dac63800 	sw	r22, r6, r7
||               974:	30c0ffff 	addik	r6, r0, -1
000.000 ns       978:	f8c30020 	swi	r6, r3, 32
||               97c:	80852000 	or	r4, r5, r4
000.000 ns       980:	f8830008 	swi	r4, r3, 8
||               984:	e9e10000 	lwi	r15, r1, 0
000.000 ns       988:	ea610004 	lwi	r19, r1, 4
||               98c:	eac10008 	lwi	r22, r1, 8
000.000 ns       990:	b60f0008 	rtsd	r15, 8
||               994:	3021000c 	addik	r1, r1, 12

00000998 <microblaze_disable_dcache>:
030.000 ns       998:	b60f0008 	rtsd	r15, 8
||               99c:	94110080 	msrclr	r0, 128

000009a0 <microblaze_disable_icache>:
030.000 ns       9a0:	b60f0008 	rtsd	r15, 8
||               9a4:	94110020 	msrclr	r0, 32

000009a8 <microblaze_flush_cache_ext>:
030.000 ns       9a8:	b60f0008 	rtsd	r15, 8
||               9ac:	80000000 	or	r0, r0, r0

000009b0 <microblaze_invalidate_cache_ext>:
060.000 ns       9b0:	b60f0008 	rtsd	r15, 8
||               9b4:	80000000 	or	r0, r0, r0

000009b8 <microblaze_invalidate_dcache>:
060.000 ns       9b8:	b000c000 	imm	-16384
||               9bc:	30a00000 	addik	r5, r0, 0
030.780 us       9c0:	30c52000 	addik	r6, r5, 8192

000009c4 <L_start>:
||               9c4:	90050064 	wdc	r5, r0
020.520 us       9c8:	16453003 	cmpu	r18, r5, r6
||               9cc:	bc72000c 	blei	r18, 12	// 9d8 <L_done>
020.480 us       9d0:	b810fff4 	brid	-12	// 9c4 <L_start>
||               9d4:	30a50010 	addik	r5, r5, 16

000009d8 <L_done>:
080.000 ns       9d8:	b60f0008 	rtsd	r15, 8
||               9dc:	80000000 	or	r0, r0, r0

000009e0 <microblaze_invalidate_icache>:
030.000 ns       9e0:	b000c000 	imm	-16384
||               9e4:	30a00000 	addik	r5, r0, 0
010.260 us       9e8:	30c52000 	addik	r6, r5, 8192

000009ec <L_start>:
||               9ec:	90050068 	wic	r5, r0
010.260 us       9f0:	16453003 	cmpu	r18, r5, r6
||               9f4:	bc72000c 	blei	r18, 12	// a00 <L_done>
010.240 us       9f8:	b810fff4 	brid	-12	// 9ec <L_start>
||               9fc:	30a50010 	addik	r5, r5, 16

00000a00 <L_done>:
040.000 ns       a00:	b60f0008 	rtsd	r15, 8
||               a04:	80000000 	or	r0, r0, r0

00000a08 <outbyte>:
390.000 ns       a08:	a4c500ff 	andi	r6, r5, 255
||               a0c:	b0004060 	imm	16480
260.000 ns       a10:	30a00000 	addik	r5, r0, 0
||               a14:	3021fffc 	addik	r1, r1, -4
260.000 ns       a18:	f9e10000 	swi	r15, r1, 0
||               a1c:	b0000000 	imm	0
260.000 ns       a20:	b9f40014 	brlid	r15, 20	// a34 <XUartLite_SendByte>
||               a24:	80000000 	or	r0, r0, r0
520.000 ns       a28:	e9e10000 	lwi	r15, r1, 0
||               a2c:	b60f0008 	rtsd	r15, 8
390.000 ns       a30:	30210004 	addik	r1, r1, 4

00000a34 <XUartLite_SendByte>:
||               a34:	30850008 	addik	r4, r5, 8
001.560 us       a38:	e8640000 	lwi	r3, r4, 0
||               a3c:	a4630008 	andi	r3, r3, 8
001.170 us       a40:	bc23fff8 	bnei	r3, -8		// a38
||               a44:	f8c50004 	swi	r6, r5, 4
260.000 ns       a48:	b60f0008 	rtsd	r15, 8
||               a4c:	80000000 	or	r0, r0, r0

00000a50 <XUartLite_RecvByte>:
000.000 ns       a50:	30850008 	addik	r4, r5, 8
||               a54:	e8640000 	lwi	r3, r4, 0
000.000 ns       a58:	a4630001 	andi	r3, r3, 1
||               a5c:	bc03fff8 	beqi	r3, -8		// a54
000.000 ns       a60:	e8650000 	lwi	r3, r5, 0
||               a64:	b60f0008 	rtsd	r15, 8
000.000 ns       a68:	a46300ff 	andi	r3, r3, 255

00000a6c <StubHandler>:
||               a6c:	bc05001c 	beqi	r5, 28		// a88
000.000 ns       a70:	e865000c 	lwi	r3, r5, 12
||               a74:	b0000000 	imm	0
000.000 ns       a78:	f8001be4 	swi	r0, r0, 7140	// 1be4 <Xil_AssertStatus>
||               a7c:	30630001 	addik	r3, r3, 1
000.000 ns       a80:	b60f0008 	rtsd	r15, 8
||               a84:	f865000c 	swi	r3, r5, 12
000.000 ns       a88:	b0000000 	imm	0
||               a8c:	30a019e4 	addik	r5, r0, 6628
000.000 ns       a90:	3021ffe4 	addik	r1, r1, -28
||               a94:	f9e10000 	swi	r15, r1, 0
000.000 ns       a98:	b0000000 	imm	0
||               a9c:	b9f40c10 	brlid	r15, 3088	// 16ac <Xil_Assert>
000.000 ns       aa0:	30c002bf 	addik	r6, r0, 703
||               aa4:	e9e10000 	lwi	r15, r1, 0
000.000 ns       aa8:	30600001 	addik	r3, r0, 1
||               aac:	b0000000 	imm	0
000.000 ns       ab0:	f8601be4 	swi	r3, r0, 7140	// 1be4 <Xil_AssertStatus>
||               ab4:	b60f0008 	rtsd	r15, 8
000.000 ns       ab8:	3021001c 	addik	r1, r1, 28

00000abc <XIntc_Initialize>:
||               abc:	3021ffd8 	addik	r1, r1, -40
000.000 ns       ac0:	f9e10000 	swi	r15, r1, 0
||               ac4:	fa61001c 	swi	r19, r1, 28
000.000 ns       ac8:	fac10020 	swi	r22, r1, 32
||               acc:	be0501a8 	beqid	r5, 424		// c74
000.000 ns       ad0:	fae10024 	swi	r23, r1, 36
||               ad4:	e8850008 	lwi	r4, r5, 8
000.000 ns       ad8:	b0000000 	imm	0
||               adc:	f8001be4 	swi	r0, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns       ae0:	b0002222 	imm	8738
||               ae4:	a8842222 	xori	r4, r4, 8738
000.000 ns       ae8:	be04001c 	beqid	r4, 28		// b04
||               aec:	30600005 	addik	r3, r0, 5
000.000 ns       af0:	b0000000 	imm	0
||               af4:	e4601a08 	lhui	r3, r0, 6664	// 1a08 <XIntc_ConfigTable>
000.000 ns       af8:	88c33000 	xor	r6, r3, r6
||               afc:	be060020 	beqid	r6, 32		// b1c
000.000 ns       b00:	30600002 	addik	r3, r0, 2
||               b04:	e9e10000 	lwi	r15, r1, 0
000.000 ns       b08:	ea61001c 	lwi	r19, r1, 28
||               b0c:	eac10020 	lwi	r22, r1, 32
000.000 ns       b10:	eae10024 	lwi	r23, r1, 36
||               b14:	b60f0008 	rtsd	r15, 8
000.000 ns       b18:	30210028 	addik	r1, r1, 40
||               b1c:	b0000000 	imm	0
000.000 ns       b20:	31001a08 	addik	r8, r0, 6664	// 1a08 <XIntc_ConfigTable>
||               b24:	b0000000 	imm	0
000.000 ns       b28:	eae01a0c 	lwi	r23, r0, 6668
||               b2c:	f8c50004 	swi	r6, r5, 4
000.000 ns       b30:	f8c50008 	swi	r6, r5, 8
||               b34:	f9050010 	swi	r8, r5, 16
000.000 ns       b38:	30600001 	addik	r3, r0, 1
||               b3c:	b0000000 	imm	0
000.000 ns       b40:	f8601a20 	swi	r3, r0, 6688
||               b44:	b0000000 	imm	0
000.000 ns       b48:	e9601a24 	lwi	r11, r0, 6692
||               b4c:	fae50000 	swi	r23, r5, 0
000.000 ns       b50:	b0000000 	imm	0
||               b54:	e9801a1c 	lwi	r12, r0, 6684
000.000 ns       b58:	be6c006c 	bleid	r12, 108		// bc4
||               b5c:	31000001 	addik	r8, r0, 1
000.000 ns       b60:	b0000000 	imm	0
||               b64:	32c016f0 	addik	r22, r0, 5872	// 16f0 <XNullHandler>
000.000 ns       b68:	10860000 	addk	r4, r6, r0
||               b6c:	12660000 	addk	r19, r6, r0
000.000 ns       b70:	31260004 	addik	r9, r6, 4
||               b74:	64e90403 	bslli	r7, r9, 3
000.000 ns       b78:	64660403 	bslli	r3, r6, 3
||               b7c:	64c60402 	bslli	r6, r6, 2
000.000 ns       b80:	b0000000 	imm	0
||               b84:	30e71a08 	addik	r7, r7, 6664
000.000 ns       b88:	e8e70000 	lwi	r7, r7, 0
||               b8c:	30840001 	addik	r4, r4, 1
000.000 ns       b90:	a48400ff 	andi	r4, r4, 255
||               b94:	89479c00 	pcmpeq	r10, r7, r19
000.000 ns       b98:	be2a008c 	bneid	r10, 140		// c24
||               b9c:	88e7b400 	pcmpeq	r7, r7, r22
000.000 ns       ba0:	bc270084 	bnei	r7, 132		// c24
||               ba4:	b0000000 	imm	0
000.000 ns       ba8:	f9061b64 	swi	r8, r6, 7012
||               bac:	b0000000 	imm	0
000.000 ns       bb0:	f8a31a2c 	swi	r5, r3, 6700
||               bb4:	11084000 	addk	r8, r8, r8
000.000 ns       bb8:	164c2001 	cmp	r18, r12, r4
||               bbc:	be52ffb4 	bltid	r18, -76		// b70
000.000 ns       bc0:	10c40000 	addk	r6, r4, r0
||               bc4:	b0000000 	imm	0
000.000 ns       bc8:	e8601a14 	lwi	r3, r0, 6676
||               bcc:	f817001c 	swi	r0, r23, 28
000.000 ns       bd0:	f8170008 	swi	r0, r23, 8
||               bd4:	3100ffff 	addik	r8, r0, -1
000.000 ns       bd8:	f917000c 	swi	r8, r23, 12
||               bdc:	a8630001 	xori	r3, r3, 1
000.000 ns       be0:	bc03005c 	beqi	r3, 92		// c3c
||               be4:	bc0b0018 	beqi	r11, 24		// bfc
000.000 ns       be8:	e8650010 	lwi	r3, r5, 16
||               bec:	b0000000 	imm	0
000.000 ns       bf0:	e8801be0 	lwi	r4, r0, 7136
||               bf4:	e8630004 	lwi	r3, r3, 4
000.000 ns       bf8:	f8830008 	swi	r4, r3, 8
||               bfc:	b0001111 	imm	4369
000.000 ns       c00:	30e01111 	addik	r7, r0, 4369
||               c04:	10600000 	addk	r3, r0, r0
000.000 ns       c08:	f8e50004 	swi	r7, r5, 4
||               c0c:	e9e10000 	lwi	r15, r1, 0
000.000 ns       c10:	ea61001c 	lwi	r19, r1, 28
||               c14:	eac10020 	lwi	r22, r1, 32
000.000 ns       c18:	eae10024 	lwi	r23, r1, 36
||               c1c:	b60f0008 	rtsd	r15, 8
000.000 ns       c20:	30210028 	addik	r1, r1, 40
||               c24:	b0000000 	imm	0
000.000 ns       c28:	30e00a6c 	addik	r7, r0, 2668	// a6c <StubHandler>
||               c2c:	65290403 	bslli	r9, r9, 3
000.000 ns       c30:	b0000000 	imm	0
||               c34:	f8e91a08 	swi	r7, r9, 6664
000.000 ns       c38:	b800ff6c 	bri	-148		// ba4
||               c3c:	10c30000 	addk	r6, r3, r0
000.000 ns       c40:	f8770020 	swi	r3, r23, 32
||               c44:	30f70100 	addik	r7, r23, 256
000.000 ns       c48:	30800020 	addik	r4, r0, 32	// 20 <_vector_hw_exception>
||               c4c:	64660402 	bslli	r3, r6, 2
000.000 ns       c50:	3084ffff 	addik	r4, r4, -1
||               c54:	31000010 	addik	r8, r0, 16	// 10 <_vector_interrupt>
000.000 ns       c58:	30c60001 	addik	r6, r6, 1
||               c5c:	d9071800 	sw	r8, r7, r3
000.000 ns       c60:	a48400ff 	andi	r4, r4, 255
||               c64:	be24ffe8 	bneid	r4, -24		// c4c
000.000 ns       c68:	a4c600ff 	andi	r6, r6, 255
||               c6c:	bc2bff7c 	bnei	r11, -132		// be8
000.000 ns       c70:	b800ff8c 	bri	-116		// bfc
||               c74:	12650000 	addk	r19, r5, r0
000.000 ns       c78:	b0000000 	imm	0
||               c7c:	30a019e4 	addik	r5, r0, 6628
000.000 ns       c80:	b0000000 	imm	0
||               c84:	b9f40a28 	brlid	r15, 2600	// 16ac <Xil_Assert>
000.000 ns       c88:	30c00090 	addik	r6, r0, 144
||               c8c:	30600001 	addik	r3, r0, 1
000.000 ns       c90:	b0000000 	imm	0
||               c94:	f8601be4 	swi	r3, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns       c98:	b810fe6c 	brid	-404		// b04
||               c9c:	10730000 	addk	r3, r19, r0

00000ca0 <XIntc_Start>:
000.000 ns       ca0:	3021ffe0 	addik	r1, r1, -32
||               ca4:	f9e10000 	swi	r15, r1, 0
000.000 ns       ca8:	be0500d8 	beqid	r5, 216		// d80
||               cac:	fa61001c 	swi	r19, r1, 28
000.000 ns       cb0:	b0000000 	imm	0
||               cb4:	f8001be4 	swi	r0, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns       cb8:	32600001 	addik	r19, r0, 1
||               cbc:	16469803 	cmpu	r18, r6, r19
000.000 ns       cc0:	bc520070 	blti	r18, 112		// d30
||               cc4:	e8650004 	lwi	r3, r5, 4
000.000 ns       cc8:	b0001111 	imm	4369
||               ccc:	a8631111 	xori	r3, r3, 4369
000.000 ns       cd0:	bc230030 	bnei	r3, 48		// d00
||               cd4:	bc26008c 	bnei	r6, 140		// d60
000.000 ns       cd8:	b0002222 	imm	8738
||               cdc:	30802222 	addik	r4, r0, 8738
000.000 ns       ce0:	e8650000 	lwi	r3, r5, 0
||               ce4:	f8850008 	swi	r4, r5, 8
000.000 ns       ce8:	fa63001c 	swi	r19, r3, 28
||               cec:	e9e10000 	lwi	r15, r1, 0
000.000 ns       cf0:	ea61001c 	lwi	r19, r1, 28
||               cf4:	10600000 	addk	r3, r0, r0
000.000 ns       cf8:	b60f0008 	rtsd	r15, 8
||               cfc:	30210020 	addik	r1, r1, 32
000.000 ns       d00:	b0000000 	imm	0
||               d04:	30a019e4 	addik	r5, r0, 6628
000.000 ns       d08:	b0000000 	imm	0
||               d0c:	b9f409a0 	brlid	r15, 2464	// 16ac <Xil_Assert>
000.000 ns       d10:	30c0012f 	addik	r6, r0, 303
||               d14:	b0000000 	imm	0
000.000 ns       d18:	fa601be4 	swi	r19, r0, 7140	// 1be4 <Xil_AssertStatus>
||               d1c:	e9e10000 	lwi	r15, r1, 0
000.000 ns       d20:	ea61001c 	lwi	r19, r1, 28
||               d24:	10600000 	addk	r3, r0, r0
000.000 ns       d28:	b60f0008 	rtsd	r15, 8
||               d2c:	30210020 	addik	r1, r1, 32
000.000 ns       d30:	b0000000 	imm	0
||               d34:	30a019e4 	addik	r5, r0, 6628
000.000 ns       d38:	b0000000 	imm	0
||               d3c:	b9f40970 	brlid	r15, 2416	// 16ac <Xil_Assert>
000.000 ns       d40:	30c0012e 	addik	r6, r0, 302
||               d44:	e9e10000 	lwi	r15, r1, 0
000.000 ns       d48:	b0000000 	imm	0
||               d4c:	fa601be4 	swi	r19, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns       d50:	ea61001c 	lwi	r19, r1, 28
||               d54:	10600000 	addk	r3, r0, r0
000.000 ns       d58:	b60f0008 	rtsd	r15, 8
||               d5c:	30210020 	addik	r1, r1, 32
000.000 ns       d60:	b0002222 	imm	8738
||               d64:	30802222 	addik	r4, r0, 8738
000.000 ns       d68:	e8650000 	lwi	r3, r5, 0
||               d6c:	32600003 	addik	r19, r0, 3
000.000 ns       d70:	f8850008 	swi	r4, r5, 8
||               d74:	fa63001c 	swi	r19, r3, 28
000.000 ns       d78:	b810ff78 	brid	-136		// cf0
||               d7c:	e9e10000 	lwi	r15, r1, 0
000.000 ns       d80:	b0000000 	imm	0
||               d84:	30a019e4 	addik	r5, r0, 6628
000.000 ns       d88:	b0000000 	imm	0
||               d8c:	b9f40920 	brlid	r15, 2336	// 16ac <Xil_Assert>
000.000 ns       d90:	30c0012c 	addik	r6, r0, 300	// 12c <__do_global_dtors_aux>
||               d94:	30600001 	addik	r3, r0, 1
000.000 ns       d98:	b0000000 	imm	0
||               d9c:	f8601be4 	swi	r3, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns       da0:	b810ff80 	brid	-128		// d20
||               da4:	e9e10000 	lwi	r15, r1, 0

00000da8 <XIntc_Stop>:
000.000 ns       da8:	3021ffe4 	addik	r1, r1, -28
||               dac:	be050064 	beqid	r5, 100		// e10
000.000 ns       db0:	f9e10000 	swi	r15, r1, 0
||               db4:	e8650004 	lwi	r3, r5, 4
000.000 ns       db8:	b0000000 	imm	0
||               dbc:	f8001be4 	swi	r0, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns       dc0:	b0001111 	imm	4369
||               dc4:	a8631111 	xori	r3, r3, 4369
000.000 ns       dc8:	bc030030 	beqi	r3, 48		// df8
||               dcc:	b0000000 	imm	0
000.000 ns       dd0:	30a019e4 	addik	r5, r0, 6628
||               dd4:	b0000000 	imm	0
000.000 ns       dd8:	b9f408d4 	brlid	r15, 2260	// 16ac <Xil_Assert>
||               ddc:	30c00166 	addik	r6, r0, 358
000.000 ns       de0:	30600001 	addik	r3, r0, 1
||               de4:	b0000000 	imm	0
000.000 ns       de8:	f8601be4 	swi	r3, r0, 7140	// 1be4 <Xil_AssertStatus>
||               dec:	e9e10000 	lwi	r15, r1, 0
000.000 ns       df0:	b60f0008 	rtsd	r15, 8
||               df4:	3021001c 	addik	r1, r1, 28
000.000 ns       df8:	e8850000 	lwi	r4, r5, 0
||               dfc:	f864001c 	swi	r3, r4, 28
000.000 ns       e00:	f8650008 	swi	r3, r5, 8
||               e04:	e9e10000 	lwi	r15, r1, 0
000.000 ns       e08:	b60f0008 	rtsd	r15, 8
||               e0c:	3021001c 	addik	r1, r1, 28
000.000 ns       e10:	b0000000 	imm	0
||               e14:	30a019e4 	addik	r5, r0, 6628
000.000 ns       e18:	b0000000 	imm	0
||               e1c:	b9f40890 	brlid	r15, 2192	// 16ac <Xil_Assert>
000.000 ns       e20:	30c00165 	addik	r6, r0, 357
||               e24:	30600001 	addik	r3, r0, 1
000.000 ns       e28:	b0000000 	imm	0
||               e2c:	f8601be4 	swi	r3, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns       e30:	b810ffc0 	brid	-64		// df0
||               e34:	e9e10000 	lwi	r15, r1, 0

00000e38 <XIntc_Connect>:
000.000 ns       e38:	3021ffe0 	addik	r1, r1, -32
||               e3c:	f9e10000 	swi	r15, r1, 0
000.000 ns       e40:	be0500c0 	beqid	r5, 192		// f00
||               e44:	fa61001c 	swi	r19, r1, 28
000.000 ns       e48:	b0000000 	imm	0
||               e4c:	f8001be4 	swi	r0, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns       e50:	32600001 	addik	r19, r0, 1
||               e54:	16469803 	cmpu	r18, r6, r19
000.000 ns       e58:	bc520078 	blti	r18, 120		// ed0
||               e5c:	bc0700cc 	beqi	r7, 204		// f28
000.000 ns       e60:	e8650004 	lwi	r3, r5, 4
||               e64:	b0001111 	imm	4369
000.000 ns       e68:	a8631111 	xori	r3, r3, 4369
||               e6c:	be230034 	bneid	r3, 52		// ea0
000.000 ns       e70:	30660004 	addik	r3, r6, 4
||               e74:	e8850010 	lwi	r4, r5, 16
000.000 ns       e78:	64630403 	bslli	r3, r3, 3
||               e7c:	64c60403 	bslli	r6, r6, 3
000.000 ns       e80:	d8e32000 	sw	r7, r3, r4
||               e84:	10c43000 	addk	r6, r4, r6
000.000 ns       e88:	f9060024 	swi	r8, r6, 36
||               e8c:	e9e10000 	lwi	r15, r1, 0
000.000 ns       e90:	ea61001c 	lwi	r19, r1, 28
||               e94:	10600000 	addk	r3, r0, r0
000.000 ns       e98:	b60f0008 	rtsd	r15, 8
||               e9c:	30210020 	addik	r1, r1, 32
000.000 ns       ea0:	b0000000 	imm	0
||               ea4:	30a019e4 	addik	r5, r0, 6628
000.000 ns       ea8:	b0000000 	imm	0
||               eac:	b9f40800 	brlid	r15, 2048	// 16ac <Xil_Assert>
000.000 ns       eb0:	30c00196 	addik	r6, r0, 406
||               eb4:	e9e10000 	lwi	r15, r1, 0
000.000 ns       eb8:	b0000000 	imm	0
||               ebc:	fa601be4 	swi	r19, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns       ec0:	ea61001c 	lwi	r19, r1, 28
||               ec4:	10600000 	addk	r3, r0, r0
000.000 ns       ec8:	b60f0008 	rtsd	r15, 8
||               ecc:	30210020 	addik	r1, r1, 32
000.000 ns       ed0:	b0000000 	imm	0
||               ed4:	30a019e4 	addik	r5, r0, 6628
000.000 ns       ed8:	b0000000 	imm	0
||               edc:	b9f407d0 	brlid	r15, 2000	// 16ac <Xil_Assert>
000.000 ns       ee0:	30c00194 	addik	r6, r0, 404
||               ee4:	e9e10000 	lwi	r15, r1, 0
000.000 ns       ee8:	b0000000 	imm	0
||               eec:	fa601be4 	swi	r19, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns       ef0:	ea61001c 	lwi	r19, r1, 28
||               ef4:	10600000 	addk	r3, r0, r0
000.000 ns       ef8:	b60f0008 	rtsd	r15, 8
||               efc:	30210020 	addik	r1, r1, 32
000.000 ns       f00:	b0000000 	imm	0
||               f04:	30a019e4 	addik	r5, r0, 6628
000.000 ns       f08:	b0000000 	imm	0
||               f0c:	b9f407a0 	brlid	r15, 1952	// 16ac <Xil_Assert>
000.000 ns       f10:	30c00193 	addik	r6, r0, 403
||               f14:	30600001 	addik	r3, r0, 1
000.000 ns       f18:	b0000000 	imm	0
||               f1c:	f8601be4 	swi	r3, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns       f20:	b810ff70 	brid	-144		// e90
||               f24:	e9e10000 	lwi	r15, r1, 0
000.000 ns       f28:	b0000000 	imm	0
||               f2c:	30a019e4 	addik	r5, r0, 6628
000.000 ns       f30:	b0000000 	imm	0
||               f34:	b9f40778 	brlid	r15, 1912	// 16ac <Xil_Assert>
000.000 ns       f38:	30c00195 	addik	r6, r0, 405
||               f3c:	b0000000 	imm	0
000.000 ns       f40:	fa601be4 	swi	r19, r0, 7140	// 1be4 <Xil_AssertStatus>
||               f44:	b810ff4c 	brid	-180		// e90
000.000 ns       f48:	e9e10000 	lwi	r15, r1, 0

00000f4c <XIntc_Disconnect>:
||               f4c:	3021ffe0 	addik	r1, r1, -32
000.000 ns       f50:	f9e10000 	swi	r15, r1, 0
||               f54:	be0500dc 	beqid	r5, 220		// 1030
000.000 ns       f58:	fa61001c 	swi	r19, r1, 28
||               f5c:	b0000000 	imm	0
000.000 ns       f60:	f8001be4 	swi	r0, r0, 7140	// 1be4 <Xil_AssertStatus>
||               f64:	32600001 	addik	r19, r0, 1
000.000 ns       f68:	16469803 	cmpu	r18, r6, r19
||               f6c:	bc520098 	blti	r18, 152		// 1004
000.000 ns       f70:	e8650004 	lwi	r3, r5, 4
||               f74:	b0001111 	imm	4369
000.000 ns       f78:	a8631111 	xori	r3, r3, 4369
||               f7c:	be23005c 	bneid	r3, 92		// fd8
000.000 ns       f80:	64860402 	bslli	r4, r6, 2
||               f84:	64660403 	bslli	r3, r6, 3
000.000 ns       f88:	e9250000 	lwi	r9, r5, 0
||               f8c:	b0000000 	imm	0
000.000 ns       f90:	30841b64 	addik	r4, r4, 7012
||               f94:	e8840000 	lwi	r4, r4, 0
000.000 ns       f98:	e8e90008 	lwi	r7, r9, 8
||               f9c:	e9050010 	lwi	r8, r5, 16
000.000 ns       fa0:	a884ffff 	xori	r4, r4, -1
||               fa4:	84843800 	and	r4, r4, r7
000.000 ns       fa8:	f8890008 	swi	r4, r9, 8
||               fac:	30c60004 	addik	r6, r6, 4
000.000 ns       fb0:	b0000000 	imm	0
||               fb4:	30800a6c 	addik	r4, r0, 2668	// a6c <StubHandler>
000.000 ns       fb8:	64c60403 	bslli	r6, r6, 3
||               fbc:	10681800 	addk	r3, r8, r3
000.000 ns       fc0:	d8864000 	sw	r4, r6, r8
||               fc4:	f8a30024 	swi	r5, r3, 36
000.000 ns       fc8:	e9e10000 	lwi	r15, r1, 0
||               fcc:	ea61001c 	lwi	r19, r1, 28
000.000 ns       fd0:	b60f0008 	rtsd	r15, 8
||               fd4:	30210020 	addik	r1, r1, 32
000.000 ns       fd8:	b0000000 	imm	0
||               fdc:	30a019e4 	addik	r5, r0, 6628
000.000 ns       fe0:	b0000000 	imm	0
||               fe4:	b9f406c8 	brlid	r15, 1736	// 16ac <Xil_Assert>
000.000 ns       fe8:	30c001cc 	addik	r6, r0, 460
||               fec:	e9e10000 	lwi	r15, r1, 0
000.000 ns       ff0:	b0000000 	imm	0
||               ff4:	fa601be4 	swi	r19, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns       ff8:	ea61001c 	lwi	r19, r1, 28
||               ffc:	b60f0008 	rtsd	r15, 8
000.000 ns      1000:	30210020 	addik	r1, r1, 32
||              1004:	b0000000 	imm	0
000.000 ns      1008:	30a019e4 	addik	r5, r0, 6628
||              100c:	b0000000 	imm	0
000.000 ns      1010:	b9f4069c 	brlid	r15, 1692	// 16ac <Xil_Assert>
||              1014:	30c001cb 	addik	r6, r0, 459
000.000 ns      1018:	e9e10000 	lwi	r15, r1, 0
||              101c:	b0000000 	imm	0
000.000 ns      1020:	fa601be4 	swi	r19, r0, 7140	// 1be4 <Xil_AssertStatus>
||              1024:	ea61001c 	lwi	r19, r1, 28
000.000 ns      1028:	b60f0008 	rtsd	r15, 8
||              102c:	30210020 	addik	r1, r1, 32
000.000 ns      1030:	b0000000 	imm	0
||              1034:	30a019e4 	addik	r5, r0, 6628
000.000 ns      1038:	b0000000 	imm	0
||              103c:	b9f40670 	brlid	r15, 1648	// 16ac <Xil_Assert>
000.000 ns      1040:	30c001ca 	addik	r6, r0, 458
||              1044:	30600001 	addik	r3, r0, 1
000.000 ns      1048:	b0000000 	imm	0
||              104c:	f8601be4 	swi	r3, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns      1050:	b810ff7c 	brid	-132		// fcc
||              1054:	e9e10000 	lwi	r15, r1, 0

00001058 <XIntc_Enable>:
000.000 ns      1058:	3021ffe0 	addik	r1, r1, -32
||              105c:	f9e10000 	swi	r15, r1, 0
000.000 ns      1060:	be0500b4 	beqid	r5, 180		// 1114
||              1064:	fa61001c 	swi	r19, r1, 28
000.000 ns      1068:	b0000000 	imm	0
||              106c:	f8001be4 	swi	r0, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns      1070:	32600001 	addik	r19, r0, 1
||              1074:	16469803 	cmpu	r18, r6, r19
000.000 ns      1078:	bc520070 	blti	r18, 112		// 10e8
||              107c:	e8650004 	lwi	r3, r5, 4
000.000 ns      1080:	b0001111 	imm	4369
||              1084:	a8631111 	xori	r3, r3, 4369
000.000 ns      1088:	be230034 	bneid	r3, 52		// 10bc
||              108c:	64c60402 	bslli	r6, r6, 2
000.000 ns      1090:	e8850000 	lwi	r4, r5, 0
||              1094:	b0000000 	imm	0
000.000 ns      1098:	30c61b64 	addik	r6, r6, 7012
||              109c:	e8a40008 	lwi	r5, r4, 8
000.000 ns      10a0:	e8660000 	lwi	r3, r6, 0
||              10a4:	80651800 	or	r3, r5, r3
000.000 ns      10a8:	f8640008 	swi	r3, r4, 8
||              10ac:	e9e10000 	lwi	r15, r1, 0
000.000 ns      10b0:	ea61001c 	lwi	r19, r1, 28
||              10b4:	b60f0008 	rtsd	r15, 8
000.000 ns      10b8:	30210020 	addik	r1, r1, 32
||              10bc:	b0000000 	imm	0
000.000 ns      10c0:	30a019e4 	addik	r5, r0, 6628
||              10c4:	b0000000 	imm	0
000.000 ns      10c8:	b9f405e4 	brlid	r15, 1508	// 16ac <Xil_Assert>
||              10cc:	30c00217 	addik	r6, r0, 535
000.000 ns      10d0:	e9e10000 	lwi	r15, r1, 0
||              10d4:	b0000000 	imm	0
000.000 ns      10d8:	fa601be4 	swi	r19, r0, 7140	// 1be4 <Xil_AssertStatus>
||              10dc:	ea61001c 	lwi	r19, r1, 28
000.000 ns      10e0:	b60f0008 	rtsd	r15, 8
||              10e4:	30210020 	addik	r1, r1, 32
000.000 ns      10e8:	b0000000 	imm	0
||              10ec:	30a019e4 	addik	r5, r0, 6628
000.000 ns      10f0:	b0000000 	imm	0
||              10f4:	b9f405b8 	brlid	r15, 1464	// 16ac <Xil_Assert>
000.000 ns      10f8:	30c00216 	addik	r6, r0, 534
||              10fc:	e9e10000 	lwi	r15, r1, 0
000.000 ns      1100:	b0000000 	imm	0
||              1104:	fa601be4 	swi	r19, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns      1108:	ea61001c 	lwi	r19, r1, 28
||              110c:	b60f0008 	rtsd	r15, 8
000.000 ns      1110:	30210020 	addik	r1, r1, 32
||              1114:	b0000000 	imm	0
000.000 ns      1118:	30a019e4 	addik	r5, r0, 6628
||              111c:	b0000000 	imm	0
000.000 ns      1120:	b9f4058c 	brlid	r15, 1420	// 16ac <Xil_Assert>
||              1124:	30c00215 	addik	r6, r0, 533
000.000 ns      1128:	30600001 	addik	r3, r0, 1
||              112c:	b0000000 	imm	0
000.000 ns      1130:	f8601be4 	swi	r3, r0, 7140	// 1be4 <Xil_AssertStatus>
||              1134:	b810ff7c 	brid	-132		// 10b0
000.000 ns      1138:	e9e10000 	lwi	r15, r1, 0

0000113c <XIntc_Disable>:
||              113c:	3021ffe0 	addik	r1, r1, -32
000.000 ns      1140:	f9e10000 	swi	r15, r1, 0
||              1144:	be0500b8 	beqid	r5, 184		// 11fc
000.000 ns      1148:	fa61001c 	swi	r19, r1, 28
||              114c:	b0000000 	imm	0
000.000 ns      1150:	f8001be4 	swi	r0, r0, 7140	// 1be4 <Xil_AssertStatus>
||              1154:	32600001 	addik	r19, r0, 1
000.000 ns      1158:	16469803 	cmpu	r18, r6, r19
||              115c:	bc520074 	blti	r18, 116		// 11d0
000.000 ns      1160:	e8650004 	lwi	r3, r5, 4
||              1164:	b0001111 	imm	4369
000.000 ns      1168:	a8631111 	xori	r3, r3, 4369
||              116c:	be230038 	bneid	r3, 56		// 11a4
000.000 ns      1170:	64c60402 	bslli	r6, r6, 2
||              1174:	e8a50000 	lwi	r5, r5, 0
000.000 ns      1178:	b0000000 	imm	0
||              117c:	30c61b64 	addik	r6, r6, 7012
000.000 ns      1180:	e8660000 	lwi	r3, r6, 0
||              1184:	e8850008 	lwi	r4, r5, 8
000.000 ns      1188:	a863ffff 	xori	r3, r3, -1
||              118c:	84632000 	and	r3, r3, r4
000.000 ns      1190:	f8650008 	swi	r3, r5, 8
||              1194:	e9e10000 	lwi	r15, r1, 0
000.000 ns      1198:	ea61001c 	lwi	r19, r1, 28
||              119c:	b60f0008 	rtsd	r15, 8
000.000 ns      11a0:	30210020 	addik	r1, r1, 32
||              11a4:	b0000000 	imm	0
000.000 ns      11a8:	30a019e4 	addik	r5, r0, 6628
||              11ac:	b0000000 	imm	0
000.000 ns      11b0:	b9f404fc 	brlid	r15, 1276	// 16ac <Xil_Assert>
||              11b4:	30c00257 	addik	r6, r0, 599
000.000 ns      11b8:	e9e10000 	lwi	r15, r1, 0
||              11bc:	b0000000 	imm	0
000.000 ns      11c0:	fa601be4 	swi	r19, r0, 7140	// 1be4 <Xil_AssertStatus>
||              11c4:	ea61001c 	lwi	r19, r1, 28
000.000 ns      11c8:	b60f0008 	rtsd	r15, 8
||              11cc:	30210020 	addik	r1, r1, 32
000.000 ns      11d0:	b0000000 	imm	0
||              11d4:	30a019e4 	addik	r5, r0, 6628
000.000 ns      11d8:	b0000000 	imm	0
||              11dc:	b9f404d0 	brlid	r15, 1232	// 16ac <Xil_Assert>
000.000 ns      11e0:	30c00256 	addik	r6, r0, 598
||              11e4:	e9e10000 	lwi	r15, r1, 0
000.000 ns      11e8:	b0000000 	imm	0
||              11ec:	fa601be4 	swi	r19, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns      11f0:	ea61001c 	lwi	r19, r1, 28
||              11f4:	b60f0008 	rtsd	r15, 8
000.000 ns      11f8:	30210020 	addik	r1, r1, 32
||              11fc:	b0000000 	imm	0
000.000 ns      1200:	30a019e4 	addik	r5, r0, 6628
||              1204:	b0000000 	imm	0
000.000 ns      1208:	b9f404a4 	brlid	r15, 1188	// 16ac <Xil_Assert>
||              120c:	30c00255 	addik	r6, r0, 597
000.000 ns      1210:	30600001 	addik	r3, r0, 1
||              1214:	b0000000 	imm	0
000.000 ns      1218:	f8601be4 	swi	r3, r0, 7140	// 1be4 <Xil_AssertStatus>
||              121c:	b810ff7c 	brid	-132		// 1198
000.000 ns      1220:	e9e10000 	lwi	r15, r1, 0

00001224 <XIntc_Acknowledge>:
||              1224:	3021ffe0 	addik	r1, r1, -32
000.000 ns      1228:	f9e10000 	swi	r15, r1, 0
||              122c:	be0500ac 	beqid	r5, 172		// 12d8
000.000 ns      1230:	fa61001c 	swi	r19, r1, 28
||              1234:	b0000000 	imm	0
000.000 ns      1238:	f8001be4 	swi	r0, r0, 7140	// 1be4 <Xil_AssertStatus>
||              123c:	32600001 	addik	r19, r0, 1
000.000 ns      1240:	16469803 	cmpu	r18, r6, r19
||              1244:	bc520068 	blti	r18, 104		// 12ac
000.000 ns      1248:	e8650004 	lwi	r3, r5, 4
||              124c:	b0001111 	imm	4369
000.000 ns      1250:	a8631111 	xori	r3, r3, 4369
||              1254:	be23002c 	bneid	r3, 44		// 1280
000.000 ns      1258:	64c60402 	bslli	r6, r6, 2
||              125c:	b0000000 	imm	0
000.000 ns      1260:	30c61b64 	addik	r6, r6, 7012
||              1264:	e8860000 	lwi	r4, r6, 0
000.000 ns      1268:	e8650000 	lwi	r3, r5, 0
||              126c:	f883000c 	swi	r4, r3, 12
000.000 ns      1270:	e9e10000 	lwi	r15, r1, 0
||              1274:	ea61001c 	lwi	r19, r1, 28
000.000 ns      1278:	b60f0008 	rtsd	r15, 8
||              127c:	30210020 	addik	r1, r1, 32
000.000 ns      1280:	b0000000 	imm	0
||              1284:	30a019e4 	addik	r5, r0, 6628
000.000 ns      1288:	b0000000 	imm	0
||              128c:	b9f40420 	brlid	r15, 1056	// 16ac <Xil_Assert>
000.000 ns      1290:	30c00293 	addik	r6, r0, 659
||              1294:	e9e10000 	lwi	r15, r1, 0
000.000 ns      1298:	b0000000 	imm	0
||              129c:	fa601be4 	swi	r19, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns      12a0:	ea61001c 	lwi	r19, r1, 28
||              12a4:	b60f0008 	rtsd	r15, 8
000.000 ns      12a8:	30210020 	addik	r1, r1, 32
||              12ac:	b0000000 	imm	0
000.000 ns      12b0:	30a019e4 	addik	r5, r0, 6628
||              12b4:	b0000000 	imm	0
000.000 ns      12b8:	b9f403f4 	brlid	r15, 1012	// 16ac <Xil_Assert>
||              12bc:	30c00292 	addik	r6, r0, 658
000.000 ns      12c0:	e9e10000 	lwi	r15, r1, 0
||              12c4:	b0000000 	imm	0
000.000 ns      12c8:	fa601be4 	swi	r19, r0, 7140	// 1be4 <Xil_AssertStatus>
||              12cc:	ea61001c 	lwi	r19, r1, 28
000.000 ns      12d0:	b60f0008 	rtsd	r15, 8
||              12d4:	30210020 	addik	r1, r1, 32
000.000 ns      12d8:	b0000000 	imm	0
||              12dc:	30a019e4 	addik	r5, r0, 6628
000.000 ns      12e0:	b0000000 	imm	0
||              12e4:	b9f403c8 	brlid	r15, 968	// 16ac <Xil_Assert>
000.000 ns      12e8:	30c00291 	addik	r6, r0, 657
||              12ec:	30600001 	addik	r3, r0, 1
000.000 ns      12f0:	b0000000 	imm	0
||              12f4:	f8601be4 	swi	r3, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns      12f8:	b810ff7c 	brid	-132		// 1274
||              12fc:	e9e10000 	lwi	r15, r1, 0

00001300 <XIntc_LookupConfig>:
000.000 ns      1300:	b0000000 	imm	0
||              1304:	e4601a08 	lhui	r3, r0, 6664	// 1a08 <XIntc_ConfigTable>
000.000 ns      1308:	88a32800 	xor	r5, r3, r5
||              130c:	bc05000c 	beqi	r5, 12		// 1318
000.000 ns      1310:	b60f0008 	rtsd	r15, 8
||              1314:	10600000 	addk	r3, r0, r0
000.000 ns      1318:	b0000000 	imm	0
||              131c:	30601a08 	addik	r3, r0, 6664	// 1a08 <XIntc_ConfigTable>
000.000 ns      1320:	b60f0008 	rtsd	r15, 8
||              1324:	80000000 	or	r0, r0, r0

00001328 <XIntc_ConnectFastHandler>:
000.000 ns      1328:	3021ffd0 	addik	r1, r1, -48
||              132c:	f9e10000 	swi	r15, r1, 0
000.000 ns      1330:	fa610020 	swi	r19, r1, 32
||              1334:	fac10024 	swi	r22, r1, 36
000.000 ns      1338:	fae10028 	swi	r23, r1, 40
||              133c:	be05018c 	beqid	r5, 396		// 14c8
000.000 ns      1340:	fb01002c 	swi	r24, r1, 44
||              1344:	b0000000 	imm	0
000.000 ns      1348:	f8001be4 	swi	r0, r0, 7140	// 1be4 <Xil_AssertStatus>
||              134c:	32c00001 	addik	r22, r0, 1
000.000 ns      1350:	1646b003 	cmpu	r18, r6, r22
||              1354:	be5200c0 	bltid	r18, 192		// 1414
000.000 ns      1358:	12e60000 	addk	r23, r6, r0
||              135c:	bc070194 	beqi	r7, 404		// 14f0
000.000 ns      1360:	e8650004 	lwi	r3, r5, 4
||              1364:	b0001111 	imm	4369
000.000 ns      1368:	a8631111 	xori	r3, r3, 4369
||              136c:	be23006c 	bneid	r3, 108		// 13d8
000.000 ns      1370:	12650000 	addk	r19, r5, r0
||              1374:	e8650010 	lwi	r3, r5, 16
000.000 ns      1378:	e863000c 	lwi	r3, r3, 12
||              137c:	a8630001 	xori	r3, r3, 1
000.000 ns      1380:	be2300d0 	bneid	r3, 208		// 1450
||              1384:	67060402 	bslli	r24, r6, 2
000.000 ns      1388:	e8650000 	lwi	r3, r5, 0
||              138c:	b0000000 	imm	0
000.000 ns      1390:	31181b64 	addik	r8, r24, 7012
||              1394:	e8830008 	lwi	r4, r3, 8
000.000 ns      1398:	eac80000 	lwi	r22, r8, 0
||              139c:	84962000 	and	r4, r22, r4
000.000 ns      13a0:	be2400ec 	bneid	r4, 236		// 148c
||              13a4:	30830100 	addik	r4, r3, 256
000.000 ns      13a8:	d8f82000 	sw	r7, r24, r4
||              13ac:	e8830020 	lwi	r4, r3, 32
000.000 ns      13b0:	82d62000 	or	r22, r22, r4
||              13b4:	fac30020 	swi	r22, r3, 32
000.000 ns      13b8:	e9e10000 	lwi	r15, r1, 0
||              13bc:	ea610020 	lwi	r19, r1, 32
000.000 ns      13c0:	eac10024 	lwi	r22, r1, 36
||              13c4:	eae10028 	lwi	r23, r1, 40
000.000 ns      13c8:	eb01002c 	lwi	r24, r1, 44
||              13cc:	10600000 	addk	r3, r0, r0
000.000 ns      13d0:	b60f0008 	rtsd	r15, 8
||              13d4:	30210030 	addik	r1, r1, 48
000.000 ns      13d8:	b0000000 	imm	0
||              13dc:	30a019e4 	addik	r5, r0, 6628
000.000 ns      13e0:	b0000000 	imm	0
||              13e4:	b9f402c8 	brlid	r15, 712	// 16ac <Xil_Assert>
000.000 ns      13e8:	30c0030d 	addik	r6, r0, 781
||              13ec:	b0000000 	imm	0
000.000 ns      13f0:	fac01be4 	swi	r22, r0, 7140	// 1be4 <Xil_AssertStatus>
||              13f4:	e9e10000 	lwi	r15, r1, 0
000.000 ns      13f8:	ea610020 	lwi	r19, r1, 32
||              13fc:	eac10024 	lwi	r22, r1, 36
000.000 ns      1400:	eae10028 	lwi	r23, r1, 40
||              1404:	eb01002c 	lwi	r24, r1, 44
000.000 ns      1408:	10600000 	addk	r3, r0, r0
||              140c:	b60f0008 	rtsd	r15, 8
000.000 ns      1410:	30210030 	addik	r1, r1, 48
||              1414:	b0000000 	imm	0
000.000 ns      1418:	30a019e4 	addik	r5, r0, 6628
||              141c:	b0000000 	imm	0
000.000 ns      1420:	b9f4028c 	brlid	r15, 652	// 16ac <Xil_Assert>
||              1424:	30c0030b 	addik	r6, r0, 779
000.000 ns      1428:	e9e10000 	lwi	r15, r1, 0
||              142c:	b0000000 	imm	0
000.000 ns      1430:	fac01be4 	swi	r22, r0, 7140	// 1be4 <Xil_AssertStatus>
||              1434:	ea610020 	lwi	r19, r1, 32
000.000 ns      1438:	eac10024 	lwi	r22, r1, 36
||              143c:	eae10028 	lwi	r23, r1, 40
000.000 ns      1440:	eb01002c 	lwi	r24, r1, 44
||              1444:	10600000 	addk	r3, r0, r0
000.000 ns      1448:	b60f0008 	rtsd	r15, 8
||              144c:	30210030 	addik	r1, r1, 48
000.000 ns      1450:	b0000000 	imm	0
||              1454:	30a019e4 	addik	r5, r0, 6628
000.000 ns      1458:	b0000000 	imm	0
||              145c:	b9f40250 	brlid	r15, 592	// 16ac <Xil_Assert>
000.000 ns      1460:	30c0030e 	addik	r6, r0, 782
||              1464:	e9e10000 	lwi	r15, r1, 0
000.000 ns      1468:	b0000000 	imm	0
||              146c:	fac01be4 	swi	r22, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns      1470:	ea610020 	lwi	r19, r1, 32
||              1474:	eac10024 	lwi	r22, r1, 36
000.000 ns      1478:	eae10028 	lwi	r23, r1, 40
||              147c:	eb01002c 	lwi	r24, r1, 44
000.000 ns      1480:	10600000 	addk	r3, r0, r0
||              1484:	b60f0008 	rtsd	r15, 8
000.000 ns      1488:	30210030 	addik	r1, r1, 48
||              148c:	b9f4fcb0 	brlid	r15, -848	// 113c <XIntc_Disable>
000.000 ns      1490:	f8e1001c 	swi	r7, r1, 28
||              1494:	e8730000 	lwi	r3, r19, 0
000.000 ns      1498:	e8e1001c 	lwi	r7, r1, 28
||              149c:	10d70000 	addk	r6, r23, r0
000.000 ns      14a0:	30830100 	addik	r4, r3, 256
||              14a4:	d8e4c000 	sw	r7, r4, r24
000.000 ns      14a8:	e8830020 	lwi	r4, r3, 32
||              14ac:	10b30000 	addk	r5, r19, r0
000.000 ns      14b0:	82d62000 	or	r22, r22, r4
||              14b4:	fac30020 	swi	r22, r3, 32
000.000 ns      14b8:	b9f4fba0 	brlid	r15, -1120	// 1058 <XIntc_Enable>
||              14bc:	80000000 	or	r0, r0, r0
000.000 ns      14c0:	b810ff38 	brid	-200		// 13f8
||              14c4:	e9e10000 	lwi	r15, r1, 0
000.000 ns      14c8:	b0000000 	imm	0
||              14cc:	30a019e4 	addik	r5, r0, 6628
000.000 ns      14d0:	b0000000 	imm	0
||              14d4:	b9f401d8 	brlid	r15, 472	// 16ac <Xil_Assert>
000.000 ns      14d8:	30c0030a 	addik	r6, r0, 778
||              14dc:	30600001 	addik	r3, r0, 1
000.000 ns      14e0:	b0000000 	imm	0
||              14e4:	f8601be4 	swi	r3, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns      14e8:	b810ff10 	brid	-240		// 13f8
||              14ec:	e9e10000 	lwi	r15, r1, 0
000.000 ns      14f0:	b0000000 	imm	0
||              14f4:	30a019e4 	addik	r5, r0, 6628
000.000 ns      14f8:	b0000000 	imm	0
||              14fc:	b9f401b0 	brlid	r15, 432	// 16ac <Xil_Assert>
000.000 ns      1500:	30c0030c 	addik	r6, r0, 780
||              1504:	b0000000 	imm	0
000.000 ns      1508:	fac01be4 	swi	r22, r0, 7140	// 1be4 <Xil_AssertStatus>
||              150c:	b810feec 	brid	-276		// 13f8
000.000 ns      1510:	e9e10000 	lwi	r15, r1, 0

00001514 <XIntc_SetNormalIntrMode>:
||              1514:	3021ffd8 	addik	r1, r1, -40
000.000 ns      1518:	f9e10000 	swi	r15, r1, 0
||              151c:	fa61001c 	swi	r19, r1, 28
000.000 ns      1520:	fac10020 	swi	r22, r1, 32
||              1524:	be050160 	beqid	r5, 352		// 1684
000.000 ns      1528:	fae10024 	swi	r23, r1, 36
||              152c:	b0000000 	imm	0
000.000 ns      1530:	f8001be4 	swi	r0, r0, 7140	// 1be4 <Xil_AssertStatus>
||              1534:	32c00001 	addik	r22, r0, 1
000.000 ns      1538:	1646b003 	cmpu	r18, r6, r22
||              153c:	bc5200d0 	blti	r18, 208		// 160c
000.000 ns      1540:	e8850004 	lwi	r4, r5, 4
||              1544:	b0001111 	imm	4369
000.000 ns      1548:	a8841111 	xori	r4, r4, 4369
||              154c:	be24008c 	bneid	r4, 140		// 15d8
000.000 ns      1550:	12650000 	addk	r19, r5, r0
||              1554:	e8850010 	lwi	r4, r5, 16
000.000 ns      1558:	e884000c 	lwi	r4, r4, 12
||              155c:	a8840001 	xori	r4, r4, 1
000.000 ns      1560:	be2400f0 	bneid	r4, 240		// 1650
||              1564:	64660402 	bslli	r3, r6, 2
000.000 ns      1568:	e8850000 	lwi	r4, r5, 0
||              156c:	b0000000 	imm	0
000.000 ns      1570:	30631b64 	addik	r3, r3, 7012
||              1574:	eac40008 	lwi	r22, r4, 8
000.000 ns      1578:	eae30000 	lwi	r23, r3, 0
||              157c:	86d7b000 	and	r22, r23, r22
000.000 ns      1580:	bc3600c0 	bnei	r22, 192		// 1640
||              1584:	e8640020 	lwi	r3, r4, 32
000.000 ns      1588:	aaf7ffff 	xori	r23, r23, -1
||              158c:	30c40100 	addik	r6, r4, 256
000.000 ns      1590:	86f71800 	and	r23, r23, r3
||              1594:	fae40020 	swi	r23, r4, 32
000.000 ns      1598:	10600000 	addk	r3, r0, r0
||              159c:	30800020 	addik	r4, r0, 32	// 20 <_vector_hw_exception>
000.000 ns      15a0:	64a30402 	bslli	r5, r3, 2
||              15a4:	3084ffff 	addik	r4, r4, -1
000.000 ns      15a8:	30e00010 	addik	r7, r0, 16	// 10 <_vector_interrupt>
||              15ac:	30630001 	addik	r3, r3, 1
000.000 ns      15b0:	d8e62800 	sw	r7, r6, r5
||              15b4:	a48400ff 	andi	r4, r4, 255
000.000 ns      15b8:	be24ffe8 	bneid	r4, -24		// 15a0
||              15bc:	a46300ff 	andi	r3, r3, 255
000.000 ns      15c0:	be160034 	beqid	r22, 52		// 15f4
||              15c4:	10b30000 	addk	r5, r19, r0
000.000 ns      15c8:	b9f4fa90 	brlid	r15, -1392	// 1058 <XIntc_Enable>
||              15cc:	30c00020 	addik	r6, r0, 32	// 20 <_vector_hw_exception>
000.000 ns      15d0:	b8100028 	brid	40		// 15f8
||              15d4:	e9e10000 	lwi	r15, r1, 0
000.000 ns      15d8:	b0000000 	imm	0
||              15dc:	30a019e4 	addik	r5, r0, 6628
000.000 ns      15e0:	b0000000 	imm	0
||              15e4:	b9f400c8 	brlid	r15, 200	// 16ac <Xil_Assert>
000.000 ns      15e8:	30c0037a 	addik	r6, r0, 890
||              15ec:	b0000000 	imm	0
000.000 ns      15f0:	fac01be4 	swi	r22, r0, 7140	// 1be4 <Xil_AssertStatus>
||              15f4:	e9e10000 	lwi	r15, r1, 0
000.000 ns      15f8:	ea61001c 	lwi	r19, r1, 28
||              15fc:	eac10020 	lwi	r22, r1, 32
000.000 ns      1600:	eae10024 	lwi	r23, r1, 36
||              1604:	b60f0008 	rtsd	r15, 8
000.000 ns      1608:	30210028 	addik	r1, r1, 40
||              160c:	b0000000 	imm	0
000.000 ns      1610:	30a019e4 	addik	r5, r0, 6628
||              1614:	b0000000 	imm	0
000.000 ns      1618:	b9f40094 	brlid	r15, 148	// 16ac <Xil_Assert>
||              161c:	30c00379 	addik	r6, r0, 889
000.000 ns      1620:	e9e10000 	lwi	r15, r1, 0
||              1624:	b0000000 	imm	0
000.000 ns      1628:	fac01be4 	swi	r22, r0, 7140	// 1be4 <Xil_AssertStatus>
||              162c:	ea61001c 	lwi	r19, r1, 28
000.000 ns      1630:	eac10020 	lwi	r22, r1, 32
||              1634:	eae10024 	lwi	r23, r1, 36
000.000 ns      1638:	b60f0008 	rtsd	r15, 8
||              163c:	30210028 	addik	r1, r1, 40
000.000 ns      1640:	b9f4fafc 	brlid	r15, -1284	// 113c <XIntc_Disable>
||              1644:	80000000 	or	r0, r0, r0
000.000 ns      1648:	b810ff3c 	brid	-196		// 1584
||              164c:	e8930000 	lwi	r4, r19, 0
000.000 ns      1650:	b0000000 	imm	0
||              1654:	30a019e4 	addik	r5, r0, 6628
000.000 ns      1658:	b0000000 	imm	0
||              165c:	b9f40050 	brlid	r15, 80	// 16ac <Xil_Assert>
000.000 ns      1660:	30c0037b 	addik	r6, r0, 891
||              1664:	e9e10000 	lwi	r15, r1, 0
000.000 ns      1668:	b0000000 	imm	0
||              166c:	fac01be4 	swi	r22, r0, 7140	// 1be4 <Xil_AssertStatus>
000.000 ns      1670:	ea61001c 	lwi	r19, r1, 28
||              1674:	eac10020 	lwi	r22, r1, 32
000.000 ns      1678:	eae10024 	lwi	r23, r1, 36
||              167c:	b60f0008 	rtsd	r15, 8
000.000 ns      1680:	30210028 	addik	r1, r1, 40
||              1684:	b0000000 	imm	0
000.000 ns      1688:	30a019e4 	addik	r5, r0, 6628
||              168c:	b0000000 	imm	0
000.000 ns      1690:	b9f4001c 	brlid	r15, 28	// 16ac <Xil_Assert>
||              1694:	30c00378 	addik	r6, r0, 888
000.000 ns      1698:	30600001 	addik	r3, r0, 1
||              169c:	b0000000 	imm	0
000.000 ns      16a0:	f8601be4 	swi	r3, r0, 7140	// 1be4 <Xil_AssertStatus>
||              16a4:	b810ff54 	brid	-172		// 15f8
000.000 ns      16a8:	e9e10000 	lwi	r15, r1, 0

000016ac <Xil_Assert>:
||              16ac:	b0000000 	imm	0
000.000 ns      16b0:	e8601b60 	lwi	r3, r0, 7008	// 1b60 <Xil_AssertCallbackRoutine>
||              16b4:	3021ffe4 	addik	r1, r1, -28
000.000 ns      16b8:	be030010 	beqid	r3, 16		// 16c8
||              16bc:	f9e10000 	swi	r15, r1, 0
000.000 ns      16c0:	99fc1800 	brald	r15, r3
||              16c4:	80000000 	or	r0, r0, r0
000.000 ns      16c8:	b0000000 	imm	0
||              16cc:	e8601a38 	lwi	r3, r0, 6712	// 1a38 <Xil_AssertWait>
000.000 ns      16d0:	be230000 	bneid	r3, 0		// 16d0
||              16d4:	e9e10000 	lwi	r15, r1, 0
000.000 ns      16d8:	b60f0008 	rtsd	r15, 8
||              16dc:	3021001c 	addik	r1, r1, 28

000016e0 <Xil_AssertSetCallback>:
000.000 ns      16e0:	b0000000 	imm	0
||              16e4:	f8a01b60 	swi	r5, r0, 7008	// 1b60 <Xil_AssertCallbackRoutine>
000.000 ns      16e8:	b60f0008 	rtsd	r15, 8
||              16ec:	80000000 	or	r0, r0, r0

000016f0 <XNullHandler>:
000.000 ns      16f0:	b60f0008 	rtsd	r15, 8
||              16f4:	80000000 	or	r0, r0, r0

000016f8 <exit>:
030.000 ns      16f8:	3021ffe0 	addik	r1, r1, -32
||              16fc:	10c00000 	addk	r6, r0, r0
020.000 ns      1700:	fa61001c 	swi	r19, r1, 28
||              1704:	f9e10000 	swi	r15, r1, 0
020.000 ns      1708:	b0000000 	imm	0
||              170c:	b9f4002c 	brlid	r15, 44	// 1738 <__call_exitprocs>
030.000 ns      1710:	12650000 	addk	r19, r5, r0
||              1714:	b0000000 	imm	0
040.000 ns      1718:	e8a019ec 	lwi	r5, r0, 6636	// 19ec <_global_impure_ptr>
||              171c:	e8650028 	lwi	r3, r5, 40
030.000 ns      1720:	bc03000c 	beqi	r3, 12		// 172c
||              1724:	99fc1800 	brald	r15, r3
030.000 ns      1728:	80000000 	or	r0, r0, r0
||              172c:	b000ffff 	imm	-1
020.000 ns      1730:	b9f4e950 	brlid	r15, -5808	// 80 <_exit>
||              1734:	10b30000 	addk	r5, r19, r0

00001738 <__call_exitprocs>:
030.000 ns      1738:	3021ffb8 	addik	r1, r1, -72
||              173c:	fb410030 	swi	r26, r1, 48
020.000 ns      1740:	b0000000 	imm	0
||              1744:	eb4019ec 	lwi	r26, r0, 6636	// 19ec <_global_impure_ptr>
020.000 ns      1748:	fb010028 	swi	r24, r1, 40
||              174c:	fb21002c 	swi	r25, r1, 44
020.000 ns      1750:	fb810038 	swi	r28, r1, 56
||              1754:	13050000 	addk	r24, r5, r0
020.000 ns      1758:	13860000 	addk	r28, r6, r0
||              175c:	b0000000 	imm	0
020.000 ns      1760:	33200000 	addik	r25, r0, 0
||              1764:	fae10024 	swi	r23, r1, 36
020.000 ns      1768:	fb610034 	swi	r27, r1, 52
||              176c:	f9e10000 	swi	r15, r1, 0
020.000 ns      1770:	fa61001c 	swi	r19, r1, 28
||              1774:	fac10020 	swi	r22, r1, 32
020.000 ns      1778:	fba1003c 	swi	r29, r1, 60
||              177c:	fbc10040 	swi	r30, r1, 64
020.000 ns      1780:	fbe10044 	swi	r31, r1, 68
||              1784:	337a0048 	addik	r27, r26, 72
020.000 ns      1788:	32e00001 	addik	r23, r0, 1
||              178c:	ebba0048 	lwi	r29, r26, 72
040.000 ns      1790:	be1d0080 	beqid	r29, 128		// 1810
||              1794:	13db0000 	addk	r30, r27, r0
000.000 ns      1798:	ea7d0004 	lwi	r19, r29, 4
||              179c:	3273ffff 	addik	r19, r19, -1
000.000 ns      17a0:	be530030 	bltid	r19, 48		// 17d0
||              17a4:	eadd0088 	lwi	r22, r29, 136
000.000 ns      17a8:	bc1c00a0 	beqi	r28, 160		// 1848
||              17ac:	be160018 	beqid	r22, 24		// 17c4
000.000 ns      17b0:	30730020 	addik	r3, r19, 32
||              17b4:	64630402 	bslli	r3, r3, 2
000.000 ns      17b8:	c863b000 	lw	r3, r3, r22
||              17bc:	887c1800 	xor	r3, r28, r3
000.000 ns      17c0:	bc030088 	beqi	r3, 136		// 1848
||              17c4:	3273ffff 	addik	r19, r19, -1
000.000 ns      17c8:	a873ffff 	xori	r3, r19, -1
||              17cc:	bc23ffdc 	bnei	r3, -36		// 17a8
000.000 ns      17d0:	be190044 	beqid	r25, 68		// 1814
||              17d4:	e9e10000 	lwi	r15, r1, 0
000.000 ns      17d8:	e87d0004 	lwi	r3, r29, 4
||              17dc:	bc23010c 	bnei	r3, 268		// 18e8
000.000 ns      17e0:	e87d0000 	lwi	r3, r29, 0
||              17e4:	bc030108 	beqi	r3, 264		// 18ec
000.000 ns      17e8:	be160014 	beqid	r22, 20		// 17fc
||              17ec:	f87e0000 	swi	r3, r30, 0
000.000 ns      17f0:	b000ffff 	imm	-1
||              17f4:	b9f4e80c 	brlid	r15, -6132	// 0 <_start>
000.000 ns      17f8:	10b60000 	addk	r5, r22, r0
||              17fc:	b000ffff 	imm	-1
000.000 ns      1800:	b9f4e800 	brlid	r15, -6144	// 0 <_start>
||              1804:	10bd0000 	addk	r5, r29, r0
000.000 ns      1808:	ebbe0000 	lwi	r29, r30, 0
||              180c:	bc3dff8c 	bnei	r29, -116		// 1798
030.000 ns      1810:	e9e10000 	lwi	r15, r1, 0
||              1814:	ea61001c 	lwi	r19, r1, 28
020.000 ns      1818:	eac10020 	lwi	r22, r1, 32
||              181c:	eae10024 	lwi	r23, r1, 36
020.000 ns      1820:	eb010028 	lwi	r24, r1, 40
||              1824:	eb21002c 	lwi	r25, r1, 44
020.000 ns      1828:	eb410030 	lwi	r26, r1, 48
||              182c:	eb610034 	lwi	r27, r1, 52
020.000 ns      1830:	eb810038 	lwi	r28, r1, 56
||              1834:	eba1003c 	lwi	r29, r1, 60
020.000 ns      1838:	ebc10040 	lwi	r30, r1, 64
||              183c:	ebe10044 	lwi	r31, r1, 68
020.000 ns      1840:	b60f0008 	rtsd	r15, 8
||              1844:	30210048 	addik	r1, r1, 72
000.000 ns      1848:	e87d0004 	lwi	r3, r29, 4
||              184c:	64b30402 	bslli	r5, r19, 2
000.000 ns      1850:	3063ffff 	addik	r3, r3, -1
||              1854:	109d2800 	addk	r4, r29, r5
000.000 ns      1858:	88639800 	xor	r3, r3, r19
||              185c:	be030074 	beqid	r3, 116		// 18d0
000.000 ns      1860:	e8e40008 	lwi	r7, r4, 8
||              1864:	f8040008 	swi	r0, r4, 8
000.000 ns      1868:	bc07ff5c 	beqi	r7, -164		// 17c4
||              186c:	be160054 	beqid	r22, 84		// 18c0
000.000 ns      1870:	ebfd0004 	lwi	r31, r29, 4
||              1874:	e8960100 	lwi	r4, r22, 256
000.000 ns      1878:	44d79c00 	bsll	r6, r23, r19
||              187c:	84862000 	and	r4, r6, r4
000.000 ns      1880:	bc040040 	beqi	r4, 64		// 18c0
||              1884:	e8760104 	lwi	r3, r22, 260
000.000 ns      1888:	84c61800 	and	r6, r6, r3
||              188c:	bc26004c 	bnei	r6, 76		// 18d8
000.000 ns      1890:	c8c5b000 	lw	r6, r5, r22
||              1894:	99fc3800 	brald	r15, r7
000.000 ns      1898:	10b80000 	addk	r5, r24, r0
||              189c:	e87d0004 	lwi	r3, r29, 4
000.000 ns      18a0:	887f1800 	xor	r3, r31, r3
||              18a4:	bc23fee8 	bnei	r3, -280		// 178c
000.000 ns      18a8:	e87e0000 	lwi	r3, r30, 0
||              18ac:	8863e800 	xor	r3, r3, r29
000.000 ns      18b0:	be03ff18 	beqid	r3, -232		// 17c8
||              18b4:	3273ffff 	addik	r19, r19, -1
000.000 ns      18b8:	b810fed8 	brid	-296		// 1790
||              18bc:	ebba0048 	lwi	r29, r26, 72
000.000 ns      18c0:	99fc3800 	brald	r15, r7
||              18c4:	80000000 	or	r0, r0, r0
000.000 ns      18c8:	b810ffd8 	brid	-40		// 18a0
||              18cc:	e87d0004 	lwi	r3, r29, 4
000.000 ns      18d0:	b810ff98 	brid	-104		// 1868
||              18d4:	fa7d0004 	swi	r19, r29, 4
000.000 ns      18d8:	99fc3800 	brald	r15, r7
||              18dc:	c8a5b000 	lw	r5, r5, r22
000.000 ns      18e0:	b810ffc0 	brid	-64		// 18a0
||              18e4:	e87d0004 	lwi	r3, r29, 4
000.000 ns      18e8:	e87d0000 	lwi	r3, r29, 0
||              18ec:	13dd0000 	addk	r30, r29, r0
000.000 ns      18f0:	13a30000 	addk	r29, r3, r0
||              18f4:	be3dfea4 	bneid	r29, -348		// 1798
000.000 ns      18f8:	e9e10000 	lwi	r15, r1, 0
||              18fc:	b810ff1c 	brid	-228		// 1818
000.000 ns      1900:	ea61001c 	lwi	r19, r1, 28

00001904 <_exception_handler>:
||              1904:	98085800 	bra	r11

00001908 <_program_clean>:
030.000 ns      1908:	b60f0008 	rtsd	r15, 8
||              190c:	80000000 	or	r0, r0, r0

00001910 <_program_init>:
030.000 ns      1910:	b60f0008 	rtsd	r15, 8
||              1914:	80000000 	or	r0, r0, r0

00001918 <__do_global_ctors_aux>:
030.000 ns      1918:	b0000000 	imm	0
||              191c:	e86019c4 	lwi	r3, r0, 6596	// 19c4 <__CTOR_LIST__>
040.000 ns      1920:	a883ffff 	xori	r4, r3, -1
||              1924:	bc04003c 	beqi	r4, 60		// 1960
000.000 ns      1928:	3021fff8 	addik	r1, r1, -8
||              192c:	fa610004 	swi	r19, r1, 4
000.000 ns      1930:	b0000000 	imm	0
||              1934:	326019c4 	addik	r19, r0, 6596	// 19c4 <__CTOR_LIST__>
000.000 ns      1938:	f9e10000 	swi	r15, r1, 0
||              193c:	99fc1800 	brald	r15, r3
000.000 ns      1940:	3273fffc 	addik	r19, r19, -4
||              1944:	e8730000 	lwi	r3, r19, 0
000.000 ns      1948:	a883ffff 	xori	r4, r3, -1
||              194c:	be24fff0 	bneid	r4, -16		// 193c
000.000 ns      1950:	e9e10000 	lwi	r15, r1, 0
||              1954:	ea610004 	lwi	r19, r1, 4
000.000 ns      1958:	b60f0008 	rtsd	r15, 8
||              195c:	30210008 	addik	r1, r1, 8
040.000 ns      1960:	b60f0008 	rtsd	r15, 8
||              1964:	80000000 	or	r0, r0, r0

Disassembly of section .init:

00001968 <__init>:
020.000 ns      1968:	3021fff8 	addik	r1, r1, -8
    196c:	d9e00800 	sw	r15, r0, r1
    1970:	3160ffff 	addik	r11, r0, -1
    1974:	940bc802 	mts	rshr, r11
    1978:	31600000 	addik	r11, r0, 0
    197c:	940bc800 	mts	rslr, r11
    1980:	b000ffff 	imm	-1
    1984:	b9f4e87c 	brlid	r15, -6020	// 200 <frame_dummy>
    1988:	80000000 	or	r0, r0, r0
    198c:	b000ffff 	imm	-1
    1990:	b9f4ff88 	brlid	r15, -120	// 1918 <__do_global_ctors_aux>
    1994:	80000000 	or	r0, r0, r0
    1998:	c9e00800 	lw	r15, r0, r1
    199c:	b60f0008 	rtsd	r15, 8
    19a0:	30210008 	addik	r1, r1, 8

Disassembly of section .fini:

000019a4 <__fini>:
    19a4:	3021fff8 	addik	r1, r1, -8
    19a8:	d9e00800 	sw	r15, r0, r1
    19ac:	b000ffff 	imm	-1
    19b0:	b9f4e77c 	brlid	r15, -6276	// 12c <__do_global_dtors_aux>
    19b4:	80000000 	or	r0, r0, r0
    19b8:	c9e00800 	lw	r15, r0, r1
    19bc:	b60f0008 	rtsd	r15, 8
    19c0:	30210008 	addik	r1, r1, 8

