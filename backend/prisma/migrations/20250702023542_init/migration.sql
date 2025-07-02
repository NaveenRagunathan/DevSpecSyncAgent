-- CreateTable
CREATE TABLE "ProjectSpec" (
    "id" TEXT NOT NULL,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,
    "problemGoal" TEXT NOT NULL,
    "mvpScope" TEXT NOT NULL,
    "dbSchema" TEXT NOT NULL,
    "apiRoutes" TEXT NOT NULL,
    "langchainDesign" TEXT NOT NULL,
    "frontendPlan" TEXT NOT NULL,
    "integrationTargets" TEXT,
    "devRoadmap" TEXT NOT NULL,

    CONSTRAINT "ProjectSpec_pkey" PRIMARY KEY ("id")
);
