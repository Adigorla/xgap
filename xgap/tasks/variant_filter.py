#!/ifshome/agorla/data_bucket/apps/python3.7.4/bin/python3

"""Variant Quality Score Recalibration"""

try:
  from subprocess import run
  from subprocess import check_output
except ImportError:
  # Python 2.7 compatibility
  from subprocess import call
  run = call

from os import path, environ, fsync
from sys import stdout, argv
from sys import exit as sysexit
from time import time
from pysam import Samfile, index, AlignmentFile

if 'SLURM_ARRAY_TASK_ID' in  environ:
    taskid = int(environ['SLURM_ARRAY_TASK_ID'])
elif 'SGE_TASK_ID' in environ:
    taskid = int(environ['SGE_TASK_ID'])
elif 'PBS_ARRAYID' in environ:
    taskid = int(environ['PBS_ARRAYID'])

if __name__ == "__main__":
  JAVA_DIR = argv[9]

def MergeVCFS(bcftools-path, in_list, out_path): 

	cmd = [bcftools-path, "concat",
		"--allow-overlaps", 
		"--remove-duplicates",
		"-0","z", 
		"-o", out_path,
		"-I"]
	cmd.extend(in_list)
	start = time()
        run(cmd, stdout=log_output, stderr=log_output)
        end = time()
        log_output.write("Merge VCFs  completed in {} seconds\n".format(end-start))
        log_output.flush()
        fsync(log_output.fileno())

def VariantFiltration(gatk_jar, in_path, out_path,log_output=stdout): 
	"""Hard-filter a large cohort callset on Excesshet using VariantFiltration""" 
	 cmd = [JAVA_DIR, "-Xmx4g", "-Xms512m","-Djava.awt.headless=true", "-jar", gatk_jar, 
		"VariantFiltration", 
		"-V", in_path, 
		"--filter-expression", ""ExcessHet > 54.69"",
		"--filter-name", "ExcesHet",
		"-O", out_path] 
	start = time()
  	run(cmd, stdout=log_output, stderr=log_output)
 	end = time()
  	log_output.write("VariantFiltration completed in {} seconds\n".format(end-start))
  	log_output.flush()
  	fsync(log_output.fileno())

def MakeSitesOnlyVCF(gatk_jar, in_path, out_path, log_output=stdout): 
	cmd = [JAVA_DIR, "-Xmx4g", "-Xms512m","-Djava.awt.headless=true", "-jar", gatk_jar,
                "MakeSitesOnlyVCF", 
		"-I", in_path, 
		"-O", out_path]
	start = time()
        run(cmd, stdout=log_output, stderr=log_output)
        end = time()
        log_output.write("MakeSitesOnlyVCF completed in {} seconds\n".format(end-start))
        log_output.flush()
        fsync(log_output.fileno())

def IndelVariantRecalibrator(gatk_jar, in_path, out_path, tranches,resource1, resource2, log_output=stdout): 
	cmd = [JAVA_DIR, "-Xmx4g", "-Xms512m","-Djava.awt.headless=true", "-jar", gatk_jar,
                "VariantRecalibrator",
		"-V", in_path, 
		"--trust-all-polymorphic",
		"-tranche 100.0", 
		"-tranche 99.95", 
		"-tranche 99.9", 
		"-tranche 99.5", 
		"-tranche 99.0", 
		"-tranche 97.0", 
		"-tranche 96.0", 
		"-tranche 95.0", 
		"-tranche 94.0",
		"-tranche 93.5", 
		"-tranche 93.0", 
		"-tranche 92.0", 
		"-tranche 91.0", 
		"-tranche 90.0",
		"-an FS -an ReadPosRankSum -an MQRankSum -an QD -an SOR -an DP",
		"-mode", "INDEL", 
		"--max-gaussians", "4",
		#Replace these with reference files, input  
		"-O", out_path, 
		"--tranches-file", tranches]
	cmd.append(''.join("-resource mills,known=false,training=true,truth=true,prior=12:",resource1))
	cmd.append(''.join("-resource dbsnp,known=true,training=false,truth=false,prior=2:",resource2))
	start = time()
        run(cmd, stdout=log_output, stderr=log_output)
        end = time()
        log_output.write("IndelVariantRecalibrator completed in {} seconds\n".format(end-start))
        log_output.flush()
        fsync(log_output.fileno())	

def SNPVariantRecalibrator(gatk_jar, in_path, out_path, tranches, resource1, resource2, log_output=stdout):
	cmd = [JAVA_DIR, "-Xmx4g", "-Xms512m","-Djava.awt.headless=true", "-jar", gatk_jar,
                "VariantRecalibrator",
		"-V", in_path, 
		"--trust-all-polymorphic"
		"-tranche 100.0 -tranche 99.95 -tranche 99.9 -tranche 99.8 -tranche 99.6 -tranche 99.5 -tranche 99.4 -tranche 99.3 -tranche 99.0 -tranche 98.0 -tranche 97.0 -tranche 90.0",
		"-an QD -an MQRankSum -an ReadPosRankSum -an FS -an MQ -an SOR -an DP",
		"-mode", "SNP", 
		"--max-gaussians", "6", 
		"-O", out_path, 
		"--tranches-file", tranches] 
	cmd.append(''.join("-resource 1000G,known=false,training=true,truth=false,prior=10:",resource1))
	cmd.append(''.join("-resource dbsnp,known=true,training=false,truth=false,prior=7:",resource2))
	start = time()
        run(cmd, stdout=log_output, stderr=log_output)
        end = time()
        log_output.write("SNPVariantRecalibrator completed in {} seconds\n".format(end-start))
        log_output.flush()
        fsync(log_output.fileno())

def IndelApplyVQSR(gatk_jar, variants, recalfile, tranches, out_path, log_output=stdout):
	cmd = [JAVA_DIR, "-Xmx4g", "-Xms512m","-Djava.awt.headless=true", "-jar", gatk_jar,
                "ApplyVQSR",
		"-V", variants, 
		"--recal-file", recalfile, 
		"--tranches-file", tranches, 
		"--truth-sensitivity-filter-level", "99.7", 
		"--create-output-variant-index", "true", 
		"-mode", "INDEL", 
		"-O", out_path]
	start = time()
        run(cmd, stdout=log_output, stderr=log_output)
        end = time()
        log_output.write("IndelApplyVQSR completed in {} seconds\n".format(end-start)) 
        log_output.write("Applying Variant Filtration\n")
        log_output.flush()
        fsync(log_output.fileno())
        vcfs="{}/vcf/{}.vcf.gz".format(out_dir, sample_id)
        output="{}/vcf/{}_merged.vcf.gz".format(out_dir, sample_id)
        fsync(log_output.fileno())

def SNPApplyVQSR(gatk_jar, variants, recalfile, tranches, out_path, log_output=stdout):
        cmd = [JAVA_DIR, "-Xmx4g", "-Xms512m","-Djava.awt.headless=true", "-jar", gatk_jar,
                "ApplyVQSR",
                "-V", variants,
                "--recal-file", recalfile,
                "--tranches-file", tranches,
		"--truth-sensitivity-filter-level", "99.7",
                "--create-output-variant-index", "true",
                "-mode", "SNP",
                "-O", out_path]
        start = time()
        run(cmd, stdout=log_output, stderr=log_output)
        end = time()
        log_output.write("SNPApplyVQSR completed in {} seconds\n".format(end-start))
        log_output.flush()
        fsync(log_output.fileno())

def main(gatk_jar, bcftools, sample_id, out_dir, log_prefix, mills, dbsnp, 1000g)
	#Merge VCFs 
	log_output.write("Merging VCFs\n")
        log_output.flush()
        fsync(log_output.fileno())
	bcftools_path=bcftools
	glob("{}/vcf/{}_region_*.vcf.gz".format(out_dir, sample_id)) 
	output="{}/vcf/{}.vcf.gz".format(out_dir, sample_id)
	MergeVCFS(bcftools_path, vcfs, output)
	#Variant Filtration
	log_output.write("Applying Variant Filtration\n")
  	log_output.flush()
  	fsync(log_output.fileno())
	cohortvcf="{}/vcf/{}.vcf.gz".format(out_dir, sample_id)
	cohortout="{}/vcf/{}_excesshet.vcf.gz".format(out_dir, sample_id)
	VariantFiltration(gatk_jar, cohortvcf, corhortout, log_output)
	#MakeSitesonlyVCF
	log_output.write("Making VCF sites\n")
        log_output.flush()
        fsync(log_output.fileno())
        cohortvcf="{}/vcf/{}_excesshet.vcf.gz".format(out_dir, sample_id)
        cohortout="{}/vcf/{}_sitesonly.vcf.gz".format(out_dir, sample_id)
        MakeSitesOnlyVCF(gatk_jar, cohortvcf, corhortout, log_output)
	#Variant Recal
	log_output.write("Calculating VQSLOD tranches for indels\n")
        log_output.flush()
        fsync(log_output.fileno())
        cohortvcf="{}/vcf/{}_sitesonly.vcf.gz".format(out_dir, sample_id)
        cohortout="{}/vcf/{}_indels.recal".format(out_dir, sample_id)
	tranches="{}/vcf/{}_indels.tranches".format(out_dir, sample_id)
        IndelVariantRecalibrator(gatk_jar, cohortvcf, corhortout, tranches, mills, dbsnp, log_output)
	log_output.write("Calculating VQSLOD tranches for snps\n")
        log_output.flush()
        fsync(log_output.fileno())
        cohortvcf="{}/vcf/{}_sitesonly.vcf.gz".format(out_dir, sample_id)
        cohortout="{}/vcf/{}_snps.recal".format(out_dir, sample_id)
        tranches="{}/vcf/{}_snps.tranches".format(out_dir, sample_id)
        SNPVariantRecalibrator(gatk_jar, cohortvcf, corhortout, tranches, 1000g, dbsnp, log_output)
	#Apply VQSR
	log_output.write("Applying VQSR to Indels\n")
        log_output.flush()
        fsync(log_output.fileno())
       	variants="{}/vcf/{}_excesshet.vcf.gz".format(out_dir, sample_id)
	recalfile="{}/vcf/{}_indels.recal".format(out_dir, sample_id)
        tranches="{}/vcf/{}_indels.tranches".format(out_dir, sample_id)
	output="{}/vcf/{}_indel.recalibrated.vcf.gz".format(out_dir, sample_id)
        IndelApplyVQSR(gatk_jar, variants, recalfile, tranches, output, log_output)
	log_output.write("Applying VQSR to SNPs\n")
        log_output.flush()
        fsync(log_output.fileno())
        variants="{}/vcf/{}_indel.recalibrated.vcf.gz".format(out_dir, sample_id)
        recalfile="{}/vcf/{}_snps.recal".format(out_dir, sample_id)
        tranches="{}/vcf/{}_snps.tranches".format(out_dir, sample_id)
        output="{}/vcf/{}_snp.recalibrated.vcf.gz".format(out_dir, sample_id)
        SNPApplyVQSR(gatk_jar, variants, recalfile, tranches,  log_output)
	sysexit(0)
#Need to add stop times
if __name__ == "__main__":
	gatk_jar = argv[1]
	bcftools = argv[2]
	sample_id = argv[3]
	out_dir = argv[4]
	log_prefix = argv[5]
        mills = argv[6]
	dbsnp = argv[7]
	1000g = argv[8]
	main(gatk_jar, bcftools, sample_id, out_dir, log_prefix, mills, dbsnp, 1000g)


