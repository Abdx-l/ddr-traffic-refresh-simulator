module trace_source;
 integer f;
 initial begin
  f=$fopen("traffic.csv","w");
  $fwrite(f,"id,arrival,bank,row,write\n");
  for(int i=0;i<256;i++) $fwrite(f,"%0d,%0d,%0d,%0d,%0d\n",i,i*2,i%4,(i/64)%16,i%3==0);
  $fclose(f);$finish;
 end
endmodule
