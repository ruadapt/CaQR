//@author Raymond Harry Rudy rudyhar@jp.ibm.com
//Counterfeit coin finding with 9 coins.
//The false coin is 6
OPENQASM 2.0;
include "qelib1.inc";
qreg qr[10];
creg cr[10];
h qr[0];
h qr[1];
h qr[2];
h qr[3];
h qr[4];
h qr[5];
h qr[6];
h qr[7];
h qr[8];
cx qr[0],qr[9];
cx qr[1],qr[9];
cx qr[2],qr[9];
cx qr[3],qr[9];
cx qr[4],qr[9];
cx qr[5],qr[9];
cx qr[6],qr[9];
cx qr[7],qr[9];
cx qr[8],qr[9];
measure qr[9] -> cr[9];


