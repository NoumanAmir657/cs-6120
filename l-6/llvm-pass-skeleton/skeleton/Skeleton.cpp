#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/IR/InstrTypes.h"
#include "llvm/IR/IRBuilder.h"
using namespace llvm;

namespace {
  struct SkeletonPass : public FunctionPass {
    static char ID;
    SkeletonPass() : FunctionPass(ID) {}

    virtual bool runOnFunction(Function &F) {
      LLVMContext& Ctx = F.getContext();

      auto printOp = F.getParent()->getOrInsertFunction(
        "printOp", Type::getVoidTy(Ctx), Type::getInt32Ty(Ctx)
      );
      
      for (auto& B: F) {
	      for (auto& I: B) {
          if (auto* op = dyn_cast<BinaryOperator>(&I)) {
            IRBuilder<> builder(op);
            builder.SetInsertPoint(&B, ++builder.GetInsertPoint());

            Value* args = {op};
            builder.CreateCall(printOp, args);
            
            return true;

            // Value* lhs = op->getOperand(0);
            // Value* rhs = op->getOperand(1);
            // Value* mul = builder.CreateMul(lhs, rhs);

            // for (auto& U: op->uses()){
            //   User* user = U.getUser();
            //   user->setOperand(U.getOperandNo(), mul);
            // }
          }
        }
      }
      return false;
    }
  };
}

char SkeletonPass::ID = 0;

// Automatically enable the pass.
// http://adriansampson.net/blog/clangpass.html
static void registerSkeletonPass(const PassManagerBuilder &,
                         legacy::PassManagerBase &PM) {
  PM.add(new SkeletonPass());
}
static RegisterStandardPasses
  RegisterMyPass(PassManagerBuilder::EP_EarlyAsPossible,
                 registerSkeletonPass);
